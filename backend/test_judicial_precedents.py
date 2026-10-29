"""
Unit & Integration Tests for Judicial Precedents & Court Records Intelligence Engine.
"""

import os
import base64
import tempfile
from pathlib import Path

TEST_DIR = tempfile.TemporaryDirectory(prefix="lexvigil-prec-")
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(TEST_DIR.name) / "test.db")
os.environ.pop("LEXVIGIL_ENV", None)

if not os.getenv("ORIGINAL_ENCRYPTION_KEY"):
    os.environ["ORIGINAL_ENCRYPTION_KEY"] = base64.b64encode(os.urandom(32)).decode()
if not os.getenv("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "test-secret-key-for-lexvigil-prec"

import pytest
from fastapi.testclient import TestClient
from backend.app import app, db, pool
from backend.judicial_records import PrecedentEngine, LANDMARK_PRECEDENTS

@pytest.fixture(scope="session", autouse=True)
def teardown_db():
    yield
    pool.shutdown(wait=True)
    db.dispose()
    TEST_DIR.cleanup()

@pytest.fixture
def auth_client():
    client = TestClient(app)
    resp = client.post(
        "/api/auth/register",
        json={"email": "advocate_prec@lexvigil.ai", "password": "safe-test-password-2026"}
    )
    assert resp.status_code == 200
    return client

def test_precedent_engine_search_and_extraction():
    engine = PrecedentEngine()
    
    # 1. Search for unilateral deduction
    hits = engine.search_precedents("unilateral deduction", mode="bm25")
    assert len(hits) > 0
    assert any("MTNL" in h["title"] or "Kailash Nath" in h["title"] for h in hits)
    
    # 2. Search with category filter
    damages_hits = engine.search_precedents("", category_filter="Liquidated Damages")
    assert len(damages_hits) > 0
    assert any("Kailash Nath" in h["title"] for h in damages_hits)

    # 3. Add custom judgment
    new_prec = engine.add_custom_judgment(
        title="Larsen & Toubro Ltd. v. State of Maharashtra",
        citation="2023 SCC OnLine Bom 1204",
        court="High Court of Bombay",
        text_content=(
            "Commercial Division Judgment:\n\n"
            "Held: In infrastructure EPC disputes, an employer cannot make arbitrary deductions "
            "from running account bills after the engineer in charge has approved the milestone. "
            "Consequently, the deduction is declared null and void."
        )
    )
    assert new_prec["id"].startswith("PREC-USER-")
    assert "arbitrary deductions" in new_prec["ratio_decidendi"].lower()

    # 4. Generate court submission sheet
    sheet = engine.generate_court_submission_sheet([hits[0]["id"]])
    assert "# SYNOPSIS OF LEGAL PRECEDENTS & AUTHORITIES" in sheet
    assert hits[0]["title"] in sheet

def test_precedent_api_endpoints(auth_client):
    client = auth_client

    # 1. GET /api/precedents
    resp = client.get("/api/precedents?q=Kailash+Nath&mode=bm25")
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) > 0
    assert "Kailash Nath" in results[0]["title"]
    assert "ratio_decidendi" in results[0]
    assert "court_submission_quote" in results[0]
    prec_id = results[0]["id"]

    # 2. GET /api/precedents/{pid}
    resp_single = client.get(f"/api/precedents/{prec_id}")
    assert resp_single.status_code == 200
    assert resp_single.json()["id"] == prec_id

    # 3. POST /api/precedents/extract
    resp_ingest = client.post(
        "/api/precedents/extract",
        json={
            "title": "Hindustan Construction Co. v. NHPC Ltd.",
            "citation": "(2020) 4 SCC 310",
            "court": "Supreme Court of India",
            "text": "Held: Liquidated damages cannot be claimed where delay was caused by employer reciprocal defaults."
        }
    )
    assert resp_ingest.status_code == 200, resp_ingest.text
    created = resp_ingest.json()
    assert created["title"] == "Hindustan Construction Co. v. NHPC Ltd."

    # 4. POST /api/precedents/submission-sheet
    resp_sheet = client.post(
        "/api/precedents/submission-sheet",
        json={"precedent_ids": [prec_id]}
    )
    assert resp_sheet.status_code == 200
    assert "markdown" in resp_sheet.json()
    assert "Kailash Nath" in resp_sheet.json()["markdown"]
