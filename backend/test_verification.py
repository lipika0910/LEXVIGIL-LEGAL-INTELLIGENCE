import pytest
from backend.engine import analyze, DEMO
from backend.verification import Review, validate_review

def fixture():
    r=analyze([{"page":None,"text":DEMO}],"test")
    a={"finding_id":r["findings"][0]["id"],"category":"Temporal","verdict":"UNCERTAIN","title":"Review needed","explanation":"Check invoice scope.","severity":"MEDIUM","evidence":[{"clause_id":"clause-1","quote":r["clauses"][0]["text"]}]}
    return r,a

def test_exact_evidence_valid():
    r,a=fixture()
    assert validate_review(r,Review(assessments=[a],limitations=[]))

def test_fabricated_quote_rejected():
    r,a=fixture();a["evidence"][0]["quote"]="fabricated evidence"
    with pytest.raises(ValueError):validate_review(r,Review(assessments=[a],limitations=[]))

def test_omitted_candidate_rejected():
    r,a=fixture()
    with pytest.raises(ValueError):validate_review(r,Review(assessments=[],limitations=[]))

def test_duplicate_assessment_rejected():
    r,a=fixture()
    with pytest.raises(ValueError):validate_review(r,Review(assessments=[a,a],limitations=[]))

def test_schema_rejects_unknown_category():
    from pydantic import ValidationError
    r,a=fixture();a["category"]="Invented"
    with pytest.raises(ValidationError):Review(assessments=[a],limitations=[])

def test_mocked_escalation_preserves_original(monkeypatch):
    from types import SimpleNamespace
    from backend.verification import semantic_review
    r,a=fixture();calls=[]
    def parse(**kwargs):
        calls.append(kwargs)
        item=dict(a)
        item["verdict"]="UNCERTAIN" if len(calls)==1 else "EXPLAINED"
        return SimpleNamespace(status="completed",output_parsed=Review(assessments=[item],limitations=["Mocked review for testing only."]))
    monkeypatch.setenv("OPENAI_CONTRACT_MODELS","first,second,third")
    out=semantic_review(r,SimpleNamespace(responses=SimpleNamespace(parse=parse)))
    assert len(calls)==2
    assert all(c["store"] is False for c in calls)
    assert out["findings"][0]["semantic"]["verdict"]=="EXPLAINED"
    assert "semantic" not in r["findings"][0]

def test_mocked_refusal_fails_closed():
    from types import SimpleNamespace
    from backend.verification import semantic_review
    r,a=fixture()
    client=SimpleNamespace(responses=SimpleNamespace(parse=lambda **kwargs:SimpleNamespace(status="completed",output_parsed=None)))
    with pytest.raises(ValueError):semantic_review(r,client)
