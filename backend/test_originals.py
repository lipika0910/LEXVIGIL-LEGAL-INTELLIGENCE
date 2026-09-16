import time
from fastapi.testclient import TestClient
from sqlalchemy import text
from backend.test_api import app, db, register, clean, release_database
from backend.app import cleanup

PAYLOAD = b'1.1 Services\nThe supplier shall provide services.\n2.1 Payment\nPayment is due in 30 days.'

def upload(client, consent=False):
    response = client.post('/api/contracts/analyze', files={'file':('contract.txt',PAYLOAD,'text/plain')}, data={'store_original':str(consent).lower()})
    assert response.status_code == 202
    aid = response.json()['id']
    for _ in range(100):
        result = client.get('/api/analyses/'+aid).json()
        if result['status']=='completed': return aid
        time.sleep(.02)
    raise AssertionError(result)

def test_original_requires_consent_and_owner_and_manual_deletion():
    with TestClient(app) as a, TestClient(app) as b:
        register(a,'original-a@example.com'); register(b,'original-b@example.com')
        no = upload(a)
        assert a.get(f'/api/analyses/{no}/original').json()=={'available':False}
        aid = upload(a, True)
        base=f'/api/analyses/{aid}/original'
        info=a.get(base).json()
        with db.connect() as con:
            stored=con.execute(text('SELECT payload,encryption_version FROM originals WHERE analysis_id=:aid'),{'aid':aid}).first()
            assert stored[1]==1 and bytes(stored[0]).startswith(b'LVENC1')
            assert PAYLOAD not in bytes(stored[0])
        assert info['available'] and info['expires']-info['consented_at']==172800
        assert b.get(base).status_code==404
        assert b.get(base+'/download').status_code==404
        assert b.delete(base).status_code==404
        result=a.get(base+'/download')
        assert result.content==PAYLOAD
        assert result.headers['content-type']=='application/octet-stream'
        assert result.headers['cache-control']=='no-store'
        assert a.post(f'/api/analyses/{aid}/save').status_code==200
        assert a.get(base).json()['expires']==info['expires']
        assert a.delete(base).status_code==200
        assert a.get(base+'/download').status_code==404
        assert a.get(f'/api/analyses/{aid}').status_code==200

def test_expiry_removes_bytes_even_for_saved_report():
    with TestClient(app) as a:
        register(a,'expiry@example.com'); aid=upload(a,True)
        a.post(f'/api/analyses/{aid}/save')
        with db.begin() as con: con.execute(text('UPDATE originals SET expires=0'))
        assert a.get(f'/api/analyses/{aid}/original/download').status_code==404
        cleanup()
        with db.connect() as con: assert con.execute(text('SELECT COUNT(*) FROM originals')).scalar()==0
        assert a.get(f'/api/analyses/{aid}').status_code==200

def test_delete_report_and_logout_remove_originals():
    with TestClient(app) as a:
        register(a,'delete@example.com'); aid=upload(a,True)
        a.delete(f'/api/analyses/{aid}')
        with db.connect() as con: assert con.execute(text('SELECT COUNT(*) FROM originals')).scalar()==0
        upload(a,True)
        a.post('/api/logout')
        with db.connect() as con: assert con.execute(text('SELECT COUNT(*) FROM originals')).scalar()==0
