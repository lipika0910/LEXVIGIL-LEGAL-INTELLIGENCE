import importlib
from fastapi.testclient import TestClient
from backend.test_api import app, clean, release_database, register
from backend.release_scope import release_scope


def test_showcase_rejects_deferred_requests_before_creating_jobs(monkeypatch):
    module = importlib.import_module('backend.app')
    monkeypatch.setattr(module, 'RELEASE_SCOPE', release_scope('showcase'))
    with TestClient(app) as client:
        register(client, 'showcase-check@example.com')
        assert client.get('/api/health').json()['release_scope']['profile'] == 'showcase'
        assert client.get('/api/ocr/options').json()['available'] is False
        for kind in ('research', 'disputes'):
            assert client.post('/api/' + kind + '/analyze', json={
                'description': 'Synthetic legal question exceeding twenty characters.'}).status_code == 409
        assert client.post('/api/analyses/synthetic/verify').status_code == 409
        for options in ({'ocr_language': 'eng'}, {'store_original': 'true'}):
            assert client.post('/api/contracts/analyze', data=options,
                files={'file': ('synthetic.txt', b'Synthetic contract', 'text/plain')}).status_code == 409
        assert client.get('/api/analyses').json() == []
