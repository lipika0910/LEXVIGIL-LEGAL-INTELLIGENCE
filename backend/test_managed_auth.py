import httpx
import pytest
from fastapi import HTTPException
from .managed_auth import ManagedAuth
from .supabase_identity import PrivateIdentity

def provider(monkeypatch, status, body):
    original = httpx.Client
    def client(**kwargs):
        return original(**kwargs, transport=httpx.MockTransport(lambda req: httpx.Response(status, json=body)))
    monkeypatch.setattr(httpx, "Client", client)
    auth = ManagedAuth("https://example.supabase.co", "sb_publishable_test")
    monkeypatch.setattr(auth, "verify", lambda header: PrivateIdentity("test-id", "a@example.com"))
    return auth

def test_confirmation_without_session(monkeypatch):
    assert provider(monkeypatch,200,{"id":"pending"}).credentials("register","a@example.com","password") is None

def test_session_is_bounded_and_refresh_not_returned(monkeypatch):
    result = provider(monkeypatch,200,{"access_token":"access","refresh_token":"secret","expires_in":7200}).credentials("login","a@example.com","password")
    assert result[1:] == ("access",3600)

@pytest.mark.parametrize("body", [{},[],{"access_token":"x","expires_in":True},{"access_token":"x","expires_in":1}])
def test_malformed_session(monkeypatch,body):
    with pytest.raises(HTTPException) as caught:
        provider(monkeypatch,200,body).credentials("login","a@example.com","password")
    assert caught.value.status_code == 503

@pytest.mark.parametrize("status,expected", [(400,400),(429,429),(500,503),(302,503)])
def test_provider_errors_are_sanitized(monkeypatch,status,expected):
    with pytest.raises(HTTPException) as caught:
        provider(monkeypatch,status,{"error":"sensitive"}).credentials("login","a@example.com","password")
    assert caught.value.status_code == expected
    assert "sensitive" not in caught.value.detail
