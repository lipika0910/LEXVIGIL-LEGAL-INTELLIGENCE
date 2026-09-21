"""Real hosted DB + real rule engine, synthetic Auth; no public deployment."""
import json
from uuid import uuid4
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import text
from backend.showcase_api import create_showcase_app
from backend.showcase_processing import process_contract
from backend.hosted_connections import create_hosted_transactions
from backend.supabase_identity import PrivateIdentity
from scripts.provision_hosted_logins import load_bundle, CA


def main():
    tx = create_hosted_transactions(load_bundle(), CA)
    user = PrivateIdentity(str(uuid4()), 'showcase@example.invalid')

    class Provider:
        url = 'https://example.invalid'
        def credentials(self, action, email, password):
            return user, 'synthetic-access-token', 3600
        def verify(self, header):
            if header != 'Bearer synthetic-access-token': raise HTTPException(401)
            return user
        def sign_out(self, access): return True

    app = create_showcase_app(tx, Provider(), 'https://testserver', process_contract)
    try:
        with TestClient(app, base_url='https://testserver', headers={'Origin':'https://testserver'}) as client:
            assert client.get('/api/me').status_code == 401
            assert client.post('/api/auth/login', json={'email':user.email,'password':'synthetic-password-2026'}).status_code == 200
            assert client.get('/api/me').json()['email'] == user.email
            assert client.post('/api/contracts/sample', headers={'Origin':'https://evil.invalid'}).status_code == 403
            assert client.post('/api/contracts/analyze', data={'ocr_language':'eng'}, files={'file':('synthetic.txt',b'x','text/plain')}).status_code == 409
            response = client.post('/api/contracts/sample')
            assert response.status_code == 200
            aid = response.json()['id']
            report = client.get('/api/analyses/'+aid).json()
            assert report['status'] == 'completed' and report['result']['kind'] == 'contract'
            assert report['result']['clauses']
            assert client.post('/api/analyses/'+aid+'/save').status_code == 200
            assert client.get('/api/analyses/'+aid).json()['saved'] == 1
            assert client.delete('/api/analyses/'+aid).status_code == 200
            assert client.get('/api/analyses/'+aid).status_code == 404
            assert client.post('/api/logout').status_code == 200
            assert client.get('/api/me').status_code == 401
        print(json.dumps({'showcase_api':'passed','database':'live restricted roles',
            'analysis':'real isolated rule engine','auth':'synthetic provider',
            'checked':['login','identity','origin denial','OCR denial','sample','report','save','delete','logout']}))
    finally:
        try:
            with tx.transaction('worker') as con:
                con.execute(text('DELETE FROM lexvigil_private.analyses WHERE owner=:owner'),{'owner':user.owner_key})
            with tx.transaction('auth') as con:
                con.execute(text('DELETE FROM lexvigil_private.sessions WHERE owner=:owner'),{'owner':user.owner_key})
        finally:
            for engine in tx.engines.values(): engine.dispose()


if __name__ == '__main__':
    try: main()
    except Exception as exc:
        print(json.dumps({'status':'failed','error_type':type(exc).__name__}))
        raise SystemExit(1) from None
