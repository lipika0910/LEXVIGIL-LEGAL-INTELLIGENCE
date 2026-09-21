"""Real hosted persistence + synthetic provider; not a live Google login test."""
import base64
import hashlib
import json
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import text
from backend.auth_flows import install_auth_flows, digest
from backend.hosted_auth import HostedAuthDatabase
from backend.hosted_connections import create_hosted_transactions
from backend.supabase_identity import PrivateIdentity
from scripts.provision_hosted_logins import load_bundle, CA


def main():
    tx = create_hosted_transactions(load_bundle(), CA)
    db = HostedAuthDatabase(tx)
    identity = PrivateIdentity(str(uuid4()), 'synthetic@example.invalid')
    flow_hashes = []

    class Provider:
        url = 'https://example.invalid'
        callback = challenge = ''
        calls = 0
        changed = False

        def send_recovery(self, email, callback, challenge):
            self.callback, self.challenge = callback, challenge

        def exchange_code(self, code, verifier):
            self.calls += 1
            assert code == 'synthetic-code'
            assert base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=') == self.challenge
            return identity, 'synthetic-access-not-a-real-token', 3600

        def verify(self, header):
            if header != 'Bearer synthetic-access-not-a-real-token':
                raise HTTPException(401)
            return identity

        def update_password(self, access, password):
            self.changed = True

        def sign_out(self, access):
            return True

    provider = Provider()
    app = FastAPI()
    install_auth_flows(app, db, lambda: provider, lambda *a: None, True,
                      'https://testserver', initialize_schema=False)
    try:
        with TestClient(app, base_url='https://testserver') as client:
            response = client.post('/api/auth/google/start')
            assert response.status_code == 200
            args = parse_qs(urlsplit(response.json()['url']).query)
            provider.challenge = args['code_challenge'][0]
            callback = args['redirect_to'][0]
            nonce = client.cookies.get('lv_google_flow')
            flow_hashes.append(digest(nonce))
            response = client.get(callback + '&code=synthetic-code', follow_redirects=False)
            assert response.headers['location'].endswith('/app/contracts')
            session = client.cookies.get('lv_session')
            with db.connect() as con:
                assert con.execute(text('SELECT owner FROM sessions WHERE token=:token'), {'token': digest(session)}).scalar_one() == identity.owner_key
            client.cookies.set('lv_google_flow', nonce, domain='testserver.local', path='/api/auth')
            response = client.get(callback + '&code=synthetic-code', follow_redirects=False)
            assert 'auth_error' in response.headers['location'] and provider.calls == 1
            assert client.post('/api/auth/recovery/start', json={'email': identity.email}).status_code == 200
            nonce = client.cookies.get('lv_recovery_flow')
            flow_hashes.append(digest(nonce))
            response = client.get(provider.callback + '&code=synthetic-code', follow_redirects=False)
            assert response.headers['location'].endswith('/reset-password')
            assert client.get('/api/auth/recovery/status').status_code == 200
            response = client.post('/api/auth/recovery/password', json={'password': 'synthetic-reset-password-2026'})
            assert response.status_code == 200 and provider.changed
            assert client.get('/api/auth/recovery/status').status_code == 401
            with db.connect() as con:
                assert con.execute(text('SELECT count(*) FROM sessions WHERE owner=:owner OR owner=:recovery'),
                    {'owner': identity.owner_key, 'recovery': 'recovery:' + identity.owner_key}).scalar_one() == 0
        print(json.dumps({'hosted_auth_routes': 'passed', 'pkce_replay_denied': True,
                          'recovery_consumed': True, 'sessions_revoked': True,
                          'provider': 'synthetic; no real Google or email call'}))
    finally:
        try:
            with db.begin() as con:
                con.execute(text('DELETE FROM sessions WHERE owner=:owner OR owner=:recovery'),
                    {'owner': identity.owner_key, 'recovery': 'recovery:' + identity.owner_key})
                for token in flow_hashes:
                    con.execute(text('DELETE FROM auth_flows WHERE token=:token'), {'token': token})
        finally:
            for engine in tx.engines.values():
                engine.dispose()


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(json.dumps({'status': 'failed', 'error_type': type(exc).__name__}))
        raise SystemExit(1) from None
