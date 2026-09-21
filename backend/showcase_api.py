"""Hosted showcase API factory. Deployment entry/configuration is separate.

No startup DDL, SQLite, background queue, original storage or AI provider.
The injected processor must provide isolated bounded text-only execution.
"""
import hashlib
import secrets
import time
from datetime import date
from pathlib import PurePath
from urllib.parse import urlsplit

from fastapi import FastAPI, Depends, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import text

from .auth_flows import install_auth_flows, digest
from .hosted_auth import HostedAuthDatabase
from .hosted_reports import HostedReports, ReportUnavailable, ShowcaseCapacityExceeded
from .release_scope import release_scope
from .engine import DEMO, TAXONOMY
from .domain import validate_contract_report
from .request_limits import RequestBodyLimit
from .showcase_slots import ShowcaseSlots

MAX_UPLOAD = 2 * 1024 * 1024


class Credentials(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=12, max_length=128)


def create_showcase_app(transactions, provider, origin, processor):
    parsed = urlsplit(origin)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:
        raise ValueError('Showcase requires an HTTPS origin without a path.')
    authdb, reports = HostedAuthDatabase(transactions), HostedReports(transactions)
    slots = ShowcaseSlots(transactions)
    app = FastAPI(title='LexVigil contract showcase', docs_url=None, openapi_url=None)
    app.add_middleware(RequestBodyLimit, maximum=MAX_UPLOAD+65536)

    def rate(key, limit=8):
        # Shared minute buckets: one transaction/advisory lock across instances.
        bucket = hashlib.sha256(key.encode()).hexdigest()
        purpose = 'rate:' + bucket
        with authdb.begin() as con:
            con.execute(text('SELECT pg_advisory_xact_lock(hashtextextended(:key,0))'), {'key': purpose})
            con.execute(text('DELETE FROM auth_flows WHERE expires<=extract(epoch FROM statement_timestamp())'))
            count = con.execute(text('SELECT count(*) FROM auth_flows WHERE purpose=:purpose'), {'purpose': purpose}).scalar_one()
            if count >= limit:
                raise HTTPException(429, 'Too many requests. Please retry in a minute.')
            con.execute(text('''INSERT INTO auth_flows(token,verifier,purpose,expires)
                VALUES (:token,'',:purpose,extract(epoch FROM statement_timestamp())+60)'''),
                {'token': secrets.token_hex(32), 'purpose': purpose})

    @app.middleware('http')
    async def guard(request, call_next):
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            if request.headers.get('origin') != origin or request.headers.get('sec-fetch-site') == 'cross-site':
                return JSONResponse({'detail': 'Origin is not allowed.'}, status_code=403)
            try:
                length = int(request.headers.get('content-length', '0'))
            except ValueError:
                return JSONResponse({'detail': 'Invalid request length.'}, status_code=400)
            if length < 0 or length > MAX_UPLOAD + 65536:
                return JSONResponse({'detail': 'Showcase upload limit is 2 MB.'}, status_code=413)
        response = await call_next(request)
        for name, value in {'Cache-Control':'no-store', 'X-Content-Type-Options':'nosniff',
                            'X-Frame-Options':'DENY', 'Referrer-Policy':'no-referrer'}.items():
            response.headers[name] = value
        if request.url.path.startswith('/api/auth/'):
            request.scope['query_string'] = b''
        return response

    @app.exception_handler(ReportUnavailable)
    async def missing(request, exc):
        return JSONResponse({'detail': 'Analysis not found or expired.'}, status_code=404)

    @app.exception_handler(ShowcaseCapacityExceeded)
    async def capacity(request, exc):
        return JSONResponse({'detail': str(exc)}, status_code=429, headers={'Retry-After': '60'})

    def identity(request: Request):
        token = request.cookies.get('lv_session', '')
        if not token or len(token) > 200:
            raise HTTPException(401, 'Please sign in.')
        with authdb.connect() as con:
            owner = con.execute(text('SELECT owner FROM sessions WHERE token=:token AND expires>extract(epoch FROM statement_timestamp())'), {'token': digest(token)}).scalar()
        if not owner or not owner.startswith('supabase:'):
            raise HTTPException(401, 'Please sign in.')
        verified = provider.verify('Bearer ' + request.cookies.get('lv_access', ''))
        if verified.owner_key != owner:
            raise HTTPException(401, 'Session identity mismatch.')
        return verified

    install_auth_flows(app, authdb, lambda: provider, rate, True, origin, initialize_schema=False)

    @app.post('/api/auth/{action}')
    def credentials(action: str, body: Credentials, request: Request, response: Response):
        if action not in ('login', 'register'):
            raise HTTPException(404)
        rate('credential-global', 30)
        rate('credential-email:' + body.email.strip().lower(), 5)
        result = provider.credentials(action, body.email.strip().lower(), body.password)
        if result is None:
            return {'requires_confirmation': True, 'message': 'Check your email for confirmation if this address is eligible.'}
        user, access, ttl = result
        token = secrets.token_urlsafe(32)
        with authdb.begin() as con:
            con.execute(text('INSERT INTO sessions(token,owner,expires) VALUES (:token,:owner,:expires)'),
                        {'token': digest(token), 'owner': user.owner_key, 'expires': time.time()+ttl})
        response.set_cookie('lv_session', token, httponly=True, secure=True, samesite='strict', max_age=ttl, path='/')
        response.set_cookie('lv_access', access, httponly=True, secure=True, samesite='strict', max_age=ttl, path='/api')
        return {'email': user.email}

    @app.get('/api/health')
    def health():
        return {'status': 'healthy', 'ai_configured': False, 'release_scope': release_scope('showcase'),
                'taxonomy': TAXONOMY, 'upload_limit_bytes': MAX_UPLOAD}

    @app.get('/api/me')
    def me(user=Depends(identity)):
        return {'email': user.email}

    @app.get('/api/ocr/options')
    def ocr(user=Depends(identity)):
        return {'available': False, 'languages': []}

    async def leased_processor(data, name, as_of):
        with slots.hold():
            return await processor(data, name, as_of)

    async def process(user, data, name, as_of):
        rate('analysis-global', 12)
        rate('analysis:' + user.owner_key, 3)
        aid = reports.reserve(user.owner_key, name)
        try:
            try:
                result = validate_contract_report(await leased_processor(data, name, as_of))
            except ValueError as exc:
                raise HTTPException(422, str(exc)[:300]) from None
            except TimeoutError:
                raise HTTPException(422, 'Document exceeded the showcase processing limit. Try a smaller document.') from None
            if not reports.complete(user.owner_key, aid, result):
                raise HTTPException(409, 'Analysis expired or was deleted.')
        except Exception:
            try:
                reports.delete(user.owner_key, aid)
            except ReportUnavailable:
                pass
            raise
        return {'id': aid}

    @app.post('/api/contracts/analyze')
    async def analyze(file: UploadFile=File(...), as_of: str=Form(''),
                      store_original: bool=Form(False), ocr_language: str=Form(''), user=Depends(identity)):
        if store_original or ocr_language:
            raise HTTPException(409, 'Original storage and OCR are deferred from this showcase.')
        if as_of:
            try: date.fromisoformat(as_of)
            except ValueError: raise HTTPException(422, 'Invalid analysis date.') from None
        name = PurePath((file.filename or 'contract').replace('\\', '/')).name[:200]
        if name.lower().rsplit('.', 1)[-1] not in ('pdf', 'docx', 'txt', 'md'):
            raise HTTPException(422, 'Upload a text-based PDF, DOCX, TXT or MD document.')
        data = await file.read(MAX_UPLOAD+1)
        await file.close()
        if not data or len(data) > MAX_UPLOAD:
            raise HTTPException(413, 'Upload a nonempty document up to 2 MB.')
        return await process(user, data, name, as_of or None)

    @app.post('/api/contracts/sample')
    async def sample(user=Depends(identity)):
        return await process(user, DEMO.encode(), 'Sample services agreement.txt', None)

    @app.get('/api/analyses')
    def history(user=Depends(identity)):
        return reports.list(user.owner_key)

    @app.get('/api/analyses/{aid}')
    def get(aid: str, user=Depends(identity)):
        return reports.get(user.owner_key, aid)

    @app.post('/api/analyses/{aid}/save')
    def save(aid: str, user=Depends(identity)):
        reports.save(user.owner_key, aid)
        return {'saved': True}

    @app.delete('/api/analyses/{aid}')
    def delete(aid: str, user=Depends(identity)):
        reports.delete(user.owner_key, aid)
        return {'deleted': True}

    @app.post('/api/logout')
    def logout(request: Request, response: Response, user=Depends(identity)):
        with transactions.transaction('worker') as con:
            con.execute(text('DELETE FROM lexvigil_private.analyses WHERE owner=:owner AND saved=0'), {'owner': user.owner_key})
        with authdb.begin() as con:
            con.execute(text('DELETE FROM sessions WHERE token=:token'), {'token': digest(request.cookies.get('lv_session',''))})
        revoked = provider.sign_out(request.cookies.get('lv_access', ''))
        response.delete_cookie('lv_session', path='/')
        response.delete_cookie('lv_access', path='/api')
        return {'ok': True, 'provider_revoked': revoked}

    return app
