import os
import hashlib
import time
import tempfile
from pathlib import Path
import pytest
import importlib
from fastapi.testclient import TestClient

TEST_DIR = tempfile.TemporaryDirectory(prefix="lexvigil-tests-")
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(TEST_DIR.name) / "test.db")
os.environ.pop("LEXVIGIL_ENV", None)
import base64
os.environ['ORIGINAL_ENCRYPTION_KEY']=base64.b64encode(os.urandom(32)).decode()
from backend.app import app, db, buckets, cleanup, pool
from sqlalchemy import text

@pytest.fixture(scope="session",autouse=True)
def release_database():
    yield
    pool.shutdown(wait=True)
    db.dispose()
    TEST_DIR.cleanup()

@pytest.fixture(autouse=True)
def clean():
    with db.begin() as con:
        for table in ("contract_jobs", "originals", "auth_flows", "analyses", "sessions", "users"):
            con.execute(text("DELETE FROM " + table))
    buckets.clear()

def register(client, email):
    r=client.post("/api/auth/register",json={"email":email,"password":"safe-test-password-2026"})
    assert r.status_code == 200
    assert "httponly" in r.headers["set-cookie"].lower()


def test_live_ai_unavailable_without_jobs_or_provider_calls(monkeypatch):
    import openai
    from backend.app import research, ResearchInput
    from backend.ai_policy import AIUnavailable
    def forbidden(*args, **kwargs):
        pytest.fail('Unapproved AI client constructed')
    monkeypatch.setattr(openai, 'OpenAI', forbidden)
    monkeypatch.setenv('OPENAI_API_KEY', 'synthetic-not-a-real-key')
    with TestClient(app) as client:
        register(client, 'india-policy@example.com')
        health = client.get('/api/health').json()
        assert health['ai_configured'] is False
        assert health['ai_policy']['code'] == 'NO_ELIGIBLE_INDIA_FREE_PROVIDER'
        for kind in ('research', 'disputes'):
            response = client.post('/api/' + kind + '/analyze', json={
                'description': 'Synthetic contract dispute for policy testing only.'})
            assert response.status_code == 503
            assert 'India-only' in response.json()['detail']
        assert client.get('/api/analyses').json() == []
        aid = completed(client)
        before = client.get('/api/analyses').json()
        assert client.post('/api/analyses/' + aid + '/verify').status_code == 503
        assert client.get('/api/analyses').json() == before
        assert client.get('/api/analyses/' + aid).json()['status'] == 'completed'
    with pytest.raises(AIUnavailable):
        research(ResearchInput(description='Synthetic research input exceeding twenty characters.'), 'research')

def completed(client):
    r=client.post("/api/contracts/sample")
    assert r.status_code == 202
    aid=r.json()["id"]
    deadline=time.monotonic()+5
    while time.monotonic()<deadline:
        result=client.get("/api/analyses/"+aid).json()
        if result["status"]=="completed": return aid
        time.sleep(.02)
    pytest.fail("Analysis did not finish")

def test_owner_isolation_and_delete():
    with TestClient(app) as a, TestClient(app) as b:
        register(a,"a@example.com"); register(b,"b@example.com")
        aid=completed(a)
        assert b.get("/api/analyses/"+aid).status_code == 404
        assert b.post("/api/analyses/"+aid+"/save").status_code == 404
        assert b.delete("/api/analyses/"+aid).status_code == 404
        assert b.get("/api/analyses").json() == []
        assert a.delete("/api/analyses/"+aid).status_code == 200
        assert a.get("/api/analyses/"+aid).status_code == 404

def test_save_logout_retention():
    with TestClient(app) as a:
        register(a,"a@example.com")
        saved=completed(a); temporary=completed(a)
        assert a.post("/api/analyses/"+saved+"/save").status_code == 200
        assert a.post("/api/logout").status_code == 200
        assert a.get("/api/me").status_code == 401
        a.post("/api/auth/login",json={"email":"a@example.com","password":"safe-test-password-2026"})
        assert a.get("/api/analyses/"+temporary).status_code == 404
        assert a.get("/api/analyses/"+saved).status_code == 200

def test_expiry_and_csrf():
    with TestClient(app) as a:
        register(a,"a@example.com"); aid=completed(a)
        assert a.post("/api/contracts/sample",headers={"origin":"https://attacker.example"}).status_code == 403
        with db.begin() as con: con.execute(text("UPDATE analyses SET expires=0"))
        cleanup()
        assert a.get("/api/analyses/"+aid).status_code == 404

def test_real_upload_and_failure():
    with TestClient(app) as a:
        register(a,"a@example.com")
        r=a.post("/api/contracts/analyze",files={"file":("contract.txt",b"1.1 Terms\nSee Section 9.9.","text/plain")},data={"as_of":"invalid"})
        assert r.status_code == 422
        assert a.post("/api/contracts/analyze",files={"file":("contract.txt",b"x","text/plain")},data={"as_of":"2026-09-12"}).status_code == 202

def test_auth_validation():
    with TestClient(app) as a:
        assert a.get("/api/analyses").status_code == 401
        assert a.post("/api/auth/register",json={"email":"bad","password":"short"}).status_code == 422
        register(a,"a@example.com")
        assert a.post("/api/auth/login",json={"email":"a@example.com","password":"incorrect-password"}).status_code == 401

def test_multilingual_evidence_survives_save_and_reload():
    payload = (Path(__file__).parent / "fixtures" / "multilingual_structure.txt").read_bytes()
    with TestClient(app) as client:
        register(client, "evidence@example.com")
        response = client.post("/api/contracts/analyze", files={"file": ("multilingual.txt", payload, "text/plain")}, data={"as_of": "2026-09-13"})
        assert response.status_code == 202
        aid = response.json()["id"]
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            row = client.get("/api/analyses/" + aid).json()
            if row["status"] in ("completed", "failed"):
                break
            time.sleep(.02)
        assert row["status"] == "completed", row.get("error")
        report = row["result"]
        assert report["schema_version"] == "1.0"
        assert report["document"]["sha256"] == hashlib.sha256(payload).hexdigest()
        assert {"Tamil", "Devanagari", "Latin"} <= set(report["document"]["scripts"])
        units = {u["id"]: u["text"] for u in report["document"]["units"]}
        for clause in report["clauses"]:
            assert clause["text"] == "\n".join(units[s["unit_id"]][s["start"]:s["end"]] for s in clause["spans"])
        assert client.post("/api/analyses/" + aid + "/save").status_code == 200
        assert client.get("/api/analyses/" + aid).json()["result"] == report

def test_managed_private_account_flow(monkeypatch):
    module = importlib.import_module("backend.app")
    from backend.supabase_identity import PrivateIdentity
    from fastapi import HTTPException
    class Provider:
        def credentials(self, action, email, password):
            if action == "register": return None
            return PrivateIdentity(email, email), email, 120
        def verify(self, header):
            token = header.removeprefix("Bearer ")
            if token not in ("a@example.com", "b@example.com"):
                raise HTTPException(401)
            return PrivateIdentity(token, token)
        def sign_out(self, access): return False
    monkeypatch.setattr(module, "AUTH_PROVIDER", "supabase")
    monkeypatch.setattr(module, "managed_auth", Provider())
    with TestClient(app) as a, TestClient(app) as b:
        pending=a.post("/api/auth/register",json={"email":"a@example.com","password":"safe-test-password"})
        assert pending.json()["requires_confirmation"]
        assert not pending.headers.get("set-cookie")
        assert a.get("/api/me").status_code == 401
        for client,email in ((a,"a@example.com"),(b,"b@example.com")):
            login=client.post("/api/auth/login",json={"email":email,"password":"safe-test-password"})
            assert login.status_code == 200
            assert "access_token" not in login.text
            assert all("HttpOnly" in h for h in login.headers.get_list("set-cookie"))
            assert client.get("/api/me").json()["email"] == email
        aid=completed(a)
        assert b.get("/api/analyses/"+aid).status_code == 404
        assert b.post("/api/analyses/"+aid+"/save").status_code == 404
        assert b.delete("/api/analyses/"+aid).status_code == 404
        previous=a.cookies.get("lv_session")
        assert a.post("/api/logout").json() == {"ok":True,"provider_revoked":False}
        a.cookies.set("lv_session",previous)
        a.cookies.set("lv_access","a@example.com",path="/api")
        assert a.get("/api/me").status_code == 401

def test_managed_mode_rejects_legacy_session(monkeypatch):
    module=importlib.import_module("backend.app")
    with TestClient(app) as client:
        register(client,"legacy@example.com")
        monkeypatch.setattr(module,"AUTH_PROVIDER","supabase")
        assert client.get("/api/me").status_code == 401
