from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from backend.health import DatabaseProbe
from backend.test_api import app, clean, release_database


def test_database_probe_caches_failure_without_leaking_secrets():
    class Broken:
        def __init__(self): self.calls=0
        def connect(self):
            self.calls+=1
            raise RuntimeError('SECRET_CONNECTION_STRING')
    db=Broken(); probe=DatabaseProbe(db)
    assert not probe.ready() and not probe.ready() and db.calls==1


def test_database_probe_success():
    db=create_engine('sqlite://')
    try: assert DatabaseProbe(db).ready()
    finally: db.dispose()


def test_liveness_and_readiness_are_distinct(monkeypatch):
    with TestClient(app) as client:
        assert client.get('/api/health/live').json()=={'status':'alive'}
        monkeypatch.setattr('backend.health.availability',lambda:{'available':True})
        ready=client.get('/api/health/ready')
        assert ready.status_code==200 and all(ready.json()['checks'].values())
        assert ready.headers['cache-control']=='no-store'
        monkeypatch.setattr('backend.health.availability',lambda:{'available':False})
        assert client.get('/api/health/ready').status_code==503
        assert client.get('/api/health/live').status_code==200


def test_missing_production_storage_cannot_report_ready(monkeypatch):
    from backend.app import originals
    with TestClient(app) as client:
        monkeypatch.setattr('backend.health.availability',lambda:{'available':True})
        monkeypatch.setattr(originals,'enabled',False)
        response=client.get('/api/health/ready')
        assert response.status_code==503
        assert response.json()['checks']['original_storage'] is False
