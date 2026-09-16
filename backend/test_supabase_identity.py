import httpx
import pytest
from fastapi import HTTPException
from .supabase_identity import SupabaseIdentityVerifier

USER = {"id": "55b183ae-8a15-4d38-9363-d4cdcf638763", "email": "private@example.com",
        "email_confirmed_at": "2026-09-13T00:00:00Z", "is_anonymous": False}

def verifier():
    return SupabaseIdentityVerifier("https://example.supabase.co", "sb_publishable_test")

def test_verified_identity_ignores_user_metadata():
    def handle(request):
        assert str(request.url) == "https://example.supabase.co/auth/v1/user"
        assert request.headers["authorization"] == "Bearer token"
        return httpx.Response(200, json={**USER, "user_metadata": {"owner": "victim", "role": "admin"}})
    identity = verifier().verify("Bearer token", transport=httpx.MockTransport(handle))
    assert identity.owner_key == "supabase:" + USER["id"]
    assert identity.email == USER["email"]

@pytest.mark.parametrize("header", ["", "token", "Basic token", "Bearer one two", "Bearer " + "x" * 16385])
def test_invalid_header_never_calls_provider(header):
    def unexpected(request):
        pytest.fail("Malformed authentication must not reach the provider")
    with pytest.raises(HTTPException) as caught:
        verifier().verify(header, transport=httpx.MockTransport(unexpected))
    assert caught.value.status_code == 401

@pytest.mark.parametrize("status,expected", [(401,401),(403,401),(429,503),(500,503),(302,503)])
def test_provider_rejection_fails_closed(status, expected):
    with pytest.raises(HTTPException) as caught:
        verifier().verify("Bearer token", transport=httpx.MockTransport(lambda r: httpx.Response(status)))
    assert caught.value.status_code == expected

@pytest.mark.parametrize("change,expected", [({"id":"victim"},503), ({"email":None},503),
    ({"is_anonymous":True},403), ({"email_confirmed_at":None},403)])
def test_invalid_or_unverified_account(change, expected):
    with pytest.raises(HTTPException) as caught:
        verifier().verify("Bearer token", transport=httpx.MockTransport(lambda r: httpx.Response(200,json={**USER,**change})))
    assert caught.value.status_code == expected

def test_timeout_is_safe_and_contains_no_token():
    def timeout(request):
        raise httpx.ReadTimeout("sensitive-token", request=request)
    with pytest.raises(HTTPException) as caught:
        verifier().verify("Bearer sensitive-token", transport=httpx.MockTransport(timeout))
    assert caught.value.status_code == 503
    assert "sensitive-token" not in caught.value.detail

@pytest.mark.parametrize("url,key", [("http://example.com","sb_publishable_test"),
    ("https://example.com/path","sb_publishable_test"),
    ("https://user@example.com","sb_publishable_test"),
    ("https://example.com","sb_secret_test")])
def test_unsafe_configuration_is_rejected(url, key):
    with pytest.raises(ValueError):
        SupabaseIdentityVerifier(url,key)
