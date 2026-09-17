import pytest
from backend.ai_policy import AIUnavailable, require_live_ai, status
from backend.verification import semantic_review


def test_key_and_claimed_region_cannot_enable_unapproved_provider(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'synthetic-not-a-real-key')
    monkeypatch.setenv('AI_REGION', 'India')
    monkeypatch.setenv('AI_FREE_ONLY', 'true')
    with pytest.raises(AIUnavailable):
        require_live_ai()
    assert status()['available'] is False
    assert status()['paid_fallback_allowed'] is False


def test_semantic_review_stops_before_provider_construction(monkeypatch):
    import openai
    def forbidden(*args, **kwargs):
        pytest.fail('An unapproved provider client was constructed')
    monkeypatch.setattr(openai, 'OpenAI', forbidden)
    with pytest.raises(AIUnavailable):
        semantic_review({})
