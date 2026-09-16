import hashlib
import base64
from urllib.parse import urlparse, parse_qs
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from .auth_flows import install_auth_flows
from .supabase_identity import PrivateIdentity

@pytest.fixture
def harness(tmp_path):
    db=create_engine('sqlite:///'+str(tmp_path/'flows.db'),connect_args={'check_same_thread':False})
    with db.begin() as con:
        con.execute(text('CREATE TABLE sessions (token TEXT PRIMARY KEY, owner TEXT, expires DOUBLE PRECISION)'))
    class Provider:
        url='https://example.supabase.co'
        changed=False
        callback=''
        challenge=''
        calls=0
        def send_recovery(self,email,callback,challenge):
            self.callback,self.challenge=callback,challenge
        def exchange_code(self,code,verifier):
            self.calls+=1
            assert code=='valid-code'
            assert base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=') == self.challenge
            return PrivateIdentity('user-1','owner@example.com'),'provider-access',3600
        def verify(self,header):
            if header!='Bearer provider-access': raise HTTPException(401)
            return PrivateIdentity('user-1','owner@example.com')
        def update_password(self,access,password): self.changed=True
        def sign_out(self,access): return True
    provider=Provider()
    app=FastAPI()
    install_auth_flows(app,db,lambda:provider,lambda *args:None,False,'http://testserver')
    with TestClient(app) as client:
        yield client,provider,db
    db.dispose()

def begin_google(client,provider):
    r=client.post('/api/auth/google/start')
    assert r.status_code==200
    args=parse_qs(urlparse(r.json()['url']).query)
    assert args['provider']==['google']
    assert args['code_challenge_method']==['s256']
    provider.challenge=args['code_challenge'][0]
    assert 'HttpOnly' in r.headers['set-cookie']
    return args['redirect_to'][0]

def test_google_pkce_cookie_session_and_replay(harness):
    client,provider,db=harness
    callback=begin_google(client,provider)
    old=client.cookies.get('lv_google_flow')
    r=client.get(callback+'&code=valid-code',follow_redirects=False)
    assert r.headers['location']=='http://testserver/app/contracts'
    assert client.cookies.get('lv_session') and client.cookies.get('lv_access')
    assert 'provider-access' not in r.text
    client.cookies.set('lv_google_flow',old,path='/api/auth')
    r=client.get(callback+'&code=valid-code',follow_redirects=False)
    assert 'auth_error' in r.headers['location']
    assert provider.calls==1

@pytest.mark.parametrize('fault',['state','cookie','expired','cancelled'])
def test_callback_failure_never_creates_session(harness,fault):
    client,provider,db=harness
    callback=begin_google(client,provider)
    if fault=='state': callback=callback.split('?')[0]+'?flow=attacker'
    if fault=='cookie': client.cookies.clear()
    if fault=='expired':
        with db.begin() as con: con.execute(text('UPDATE auth_flows SET expires=0'))
    suffix='&error=access_denied' if fault=='cancelled' else '&code=valid-code'
    r=client.get(callback+suffix,follow_redirects=False)
    assert 'auth_error' in r.headers['location']
    assert not client.cookies.get('lv_session')
    assert provider.calls==0

def test_recovery_is_restricted_single_use_and_revokes_sessions(harness):
    client,provider,db=harness
    client.post('/api/auth/recovery/start',json={'email':'owner@example.com'})
    r=client.get(provider.callback+'&code=valid-code',follow_redirects=False)
    assert r.headers['location']=='http://testserver/reset-password'
    assert not client.cookies.get('lv_session')
    assert not client.cookies.get('lv_access')
    with db.begin() as con:
        con.execute(text("INSERT INTO sessions VALUES ('old','supabase:user-1',9999999999)"))
    assert client.get('/api/auth/recovery/status').status_code==200
    r=client.post('/api/auth/recovery/password',json={'password':'new-safe-password-2026'})
    assert r.status_code==200 and provider.changed
    with db.connect() as con: assert con.execute(text('SELECT count(*) FROM sessions')).scalar()==0
    assert client.post('/api/auth/recovery/password',json={'password':'new-safe-password-2026'}).status_code==401

def test_bad_email_and_no_reset_session(harness):
    client,provider,db=harness
    assert client.post('/api/auth/recovery/start',json={'email':'bad'}).status_code==422
    assert client.get('/api/auth/recovery/status').status_code==401
    assert client.post('/api/auth/recovery/password',json={'password':'long-enough-password'}).status_code==401
