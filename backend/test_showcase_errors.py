from unittest.mock import Mock
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from backend.showcase_api import create_showcase_app


@pytest.mark.parametrize('error', [RuntimeError('private-secret-detail'), SQLAlchemyError('private-secret-detail')])
def test_unexpected_errors_are_redacted(error, caplog):
    app=create_showcase_app(Mock(),Mock(),'https://example.test',Mock())
    @app.get('/synthetic-failure')
    def fail():
        raise error
    with TestClient(app) as client:
        response=client.get('/synthetic-failure')
    assert response.status_code==503
    assert 'private-secret-detail' not in response.text
    assert 'private-secret-detail' not in caplog.text
    assert response.headers['cache-control']=='no-store'
    assert response.headers['x-content-type-options']=='nosniff'


def test_expected_auth_rejection_and_origin_denial_remain_safe():
    app=create_showcase_app(Mock(),Mock(),'https://example.test',Mock())
    with TestClient(app) as client:
        assert client.get('/api/me').status_code==401
        denied=client.post('/api/contracts/sample',headers={'Origin':'https://wrong.test'})
        assert denied.status_code==403
        assert denied.headers['cache-control']=='no-store'
