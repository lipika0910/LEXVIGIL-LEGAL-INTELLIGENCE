"""Single-use PKCE flows and isolated password recovery for private accounts."""
import base64
import hashlib
import hmac
import logging
import re
import secrets
import time
from urllib.parse import urlencode, urlsplit
from fastapi import HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy import text

class RecoveryEmail(BaseModel):
    email: str = Field(min_length=3, max_length=254)

class NewPassword(BaseModel):
    password: str = Field(min_length=12, max_length=128)

def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()

def install_auth_flows(app, db, get_provider, rate, secure, origin, *, initialize_schema=True):
    parsed = urlsplit(origin)
    if parsed.scheme not in ('http','https') or not parsed.netloc or parsed.path not in ('','/') or parsed.query or parsed.fragment or parsed.username:
        raise RuntimeError('APP_ORIGIN must be an origin without a path.')
    if secure and parsed.scheme != 'https':
        raise RuntimeError('Production authentication requires HTTPS.')
    origin = origin.rstrip('/')
    if initialize_schema:
        with db.begin() as con:
            con.execute(text('CREATE TABLE IF NOT EXISTS auth_flows (token TEXT PRIMARY KEY, verifier TEXT NOT NULL, purpose TEXT NOT NULL, expires DOUBLE PRECISION NOT NULL)'))

    def provider():
        value = get_provider()
        if not value: raise HTTPException(503, 'Managed authentication is not configured.')
        return value

    def cookie(response, name, value, ttl, path='/api/auth'):
        response.set_cookie(name, value, httponly=True, secure=secure, samesite='lax', max_age=ttl, path=path)

    def create_flow(purpose, response):
        nonce, verifier = secrets.token_urlsafe(32), secrets.token_urlsafe(48)
        with db.begin() as con:
            con.execute(text('DELETE FROM auth_flows WHERE expires<=:now'), {'now':time.time()})
            con.execute(text('INSERT INTO auth_flows VALUES (:token,:verifier,:purpose,:expires)'),
                {'token':digest(nonce),'verifier':verifier,'purpose':purpose,'expires':time.time()+600})
        cookie(response, 'lv_'+purpose+'_flow', nonce, 600)
        callback = origin + '/api/auth/' + purpose + '/callback?' + urlencode({'flow':nonce})
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
        return callback, challenge

    def consume_flow(request, purpose):
        nonce = request.cookies.get('lv_'+purpose+'_flow','')
        flow = request.query_params.get('flow','')
        if not nonce or len(flow)>200 or not hmac.compare_digest(nonce,flow):
            raise HTTPException(400, 'Invalid authentication flow.')
        with db.begin() as con:
            verifier = con.execute(text('DELETE FROM auth_flows WHERE token=:token AND purpose=:purpose AND expires>:now RETURNING verifier'),
                {'token':digest(nonce),'purpose':purpose,'now':time.time()}).scalar()
        if not verifier: raise HTTPException(400, 'Authentication flow expired or already used.')
        code = request.query_params.get('code','')
        if request.query_params.get('error') or not code or len(code)>4096:
            raise HTTPException(400, 'Authentication was cancelled or expired.')
        return verifier, code

    def issue_session(response, identity, access, ttl, recovery=False):
        token = secrets.token_urlsafe(32)
        ttl = min(ttl,600) if recovery else ttl
        owner = ('recovery:' if recovery else '') + identity.owner_key
        with db.begin() as con:
            con.execute(text('INSERT INTO sessions VALUES (:token,:owner,:expires)'),
                {'token':digest(token),'owner':owner,'expires':time.time()+ttl})
        if recovery:
            cookie(response,'lv_recovery',token,ttl,'/api/auth/recovery')
            cookie(response,'lv_recovery_access',access,ttl,'/api/auth/recovery')
        else:
            response.set_cookie('lv_session',token,httponly=True,secure=secure,samesite='strict',max_age=ttl,path='/')
            response.set_cookie('lv_access',access,httponly=True,secure=secure,samesite='strict',max_age=ttl,path='/api')

    @app.get('/api/auth/options')
    def options():
        return {'managed':get_provider() is not None}

    @app.post('/api/auth/google/start')
    def google_start(request:Request,response:Response):
        auth = provider()
        rate('oauth:'+str(request.client.host),8)
        callback, challenge = create_flow('google',response)
        return {'url':auth.url+'/auth/v1/authorize?'+urlencode({'provider':'google','redirect_to':callback,
            'code_challenge':challenge,'code_challenge_method':'s256','scopes':'email profile'})}

    @app.post('/api/auth/recovery/start')
    def recovery_start(body:RecoveryEmail,request:Request,response:Response):
        auth = provider()
        rate('recovery:'+str(request.client.host),3)
        email = body.email.strip().lower()
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email): raise HTTPException(422,'Enter a valid email address.')
        callback, challenge = create_flow('recovery',response)
        auth.send_recovery(email,callback,challenge)
        return {'message':'If this address is eligible, a reset email will arrive. Open the newest link in this same browser within 10 minutes.'}

    def finish(request,purpose):
        stage = 'provider'
        try:
            auth = provider()
            stage = 'flow'
            verifier, code = consume_flow(request,purpose)
            stage = 'exchange'
            identity,access,ttl = auth.exchange_code(code,verifier)
            target = '/reset-password' if purpose=='recovery' else '/app/contracts'
            response = RedirectResponse(origin+target,status_code=303)
            stage = 'session'
            issue_session(response,identity,access,ttl,purpose=='recovery')
            logging.getLogger(__name__).info('Auth callback completed (%s)', purpose)
        except HTTPException as exc:
            # Fixed labels and booleans only, never credentials or identities.
            logging.getLogger(__name__).warning(
                'Auth callback rejected purpose=%s stage=%s status=%s flow_cookie=%s flow_query=%s code=%s provider_error=%s',
                purpose, stage, exc.status_code,
                bool(request.cookies.get('lv_'+purpose+'_flow')),
                bool(request.query_params.get('flow')),
                bool(request.query_params.get('code')),
                bool(request.query_params.get('error')),
            )
            response = RedirectResponse(origin+'/login?auth_error=flow_failed',status_code=303)
        response.delete_cookie('lv_'+purpose+'_flow',path='/api/auth')
        return response

    @app.get('/api/auth/google/callback')
    def google_callback(request:Request):
        return finish(request,'google')

    @app.get('/api/auth/recovery/callback')
    def recovery_callback(request:Request):
        return finish(request,'recovery')

    def recovery_owner(request, consume=False):
        token = request.cookies.get('lv_recovery','')
        query = ('DELETE FROM sessions WHERE token=:token AND expires>:now RETURNING owner' if consume
                 else 'SELECT owner FROM sessions WHERE token=:token AND expires>:now')
        with db.begin() as con:
            owner = con.execute(text(query),{'token':digest(token),'now':time.time()}).scalar()
        if not owner or not owner.startswith('recovery:supabase:'):
            raise HTTPException(401,'Open a new password-reset link in the browser where you requested it.')
        return owner.removeprefix('recovery:')

    @app.get('/api/auth/recovery/status')
    def recovery_status(request:Request):
        recovery_owner(request)
        return {'ready':True}

    @app.post('/api/auth/recovery/password')
    def recovery_password(body:NewPassword,request:Request,response:Response):
        auth = provider()
        rate('reset:'+str(request.client.host),5)
        access = request.cookies.get('lv_recovery_access','')
        identity = auth.verify('Bearer '+access)
        uid = recovery_owner(request,consume=True)
        if identity.owner_key != uid: raise HTTPException(401,'Recovery identity mismatch.')
        auth.update_password(access,body.password)
        with db.begin() as con:
            con.execute(text('DELETE FROM sessions WHERE owner=:uid OR owner=:recovery'),{'uid':uid,'recovery':'recovery:'+uid})
        auth.sign_out(access)
        for name in ('lv_recovery','lv_recovery_access'):
            response.delete_cookie(name,path='/api/auth/recovery')
        response.delete_cookie('lv_session',path='/')
        response.delete_cookie('lv_access',path='/api')
        return {'message':'Password updated. Sign in with your new password.'}
