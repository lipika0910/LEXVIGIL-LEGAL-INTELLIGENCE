"""
Comprehensive End-to-End Integration Test for LexVigil AI Legal Intelligence Platform.
Validates the entire integrated lifecycle:
1. User registration & session authentication
2. Loading fictional demonstration case (Apex v. Metro Rail)
3. Document ingestion, metadata, and automated fact extraction
4. Facts management and confirmation
5. Evidence graph querying and manual relationship linking
6. Pathfinding algorithms: BFS, DFS, UCS, A*, Greedy Best-First
7. Intelligent search: BM25, TF-IDF, exact substring, phrase search
8. Timeline reconstruction and inconsistency detection/resolution
9. Knowledge reasoning: Forward chaining fixpoint deduction & Backward chaining goal proofs
10. Legal arguments, counterarguments, and authorities registry
11. Case preparation report brief generation
12. Interactive AI Algorithm Lab endpoints (Search, Games, Logic, CSP, ML, RL)
13. Preserved contract analysis regression check
"""

import os
import base64
import tempfile
from pathlib import Path

TEST_DIR = tempfile.TemporaryDirectory(prefix="lexvigil-e2e-")
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(TEST_DIR.name) / "test.db")
os.environ.pop("LEXVIGIL_ENV", None)

if not os.getenv("ORIGINAL_ENCRYPTION_KEY"):
    os.environ["ORIGINAL_ENCRYPTION_KEY"] = base64.b64encode(os.urandom(32)).decode()
if not os.getenv("SECRET_KEY"):
    os.environ["SECRET_KEY"] = "test-secret-key-for-lexvigil-e2e"

import pytest
from fastapi.testclient import TestClient
from backend.app import app, db, pool

@pytest.fixture(scope="session", autouse=True)
def teardown_db():
    yield
    pool.shutdown(wait=True)
    db.dispose()
    TEST_DIR.cleanup()

@pytest.fixture
def auth_client():
    client = TestClient(app)
    # Register test advocate user (creates session cookie lv_session)
    resp = client.post(
        "/api/auth/register",
        json={"email": "advocate_e2e@lexvigil.ai", "password": "safe-test-password-2026"}
    )
    assert resp.status_code == 200, resp.text
    assert "lv_session" in resp.cookies or "set-cookie" in resp.headers
    return client

def test_full_legal_intelligence_e2e_workflow(auth_client):
    client = auth_client

    # 1. 1-Click Load Fictional Demonstration Case
    resp = client.post("/api/cases/demo")
    assert resp.status_code == 200, resp.text
    demo_data = resp.json()
    case_id = demo_data["id"]
    assert case_id is not None
    assert "Apex Infrastructure" in demo_data["title"]
    assert demo_data["doc_count"] == 6

    # 2. Case Workspace Overview & Metadata
    resp = client.get(f"/api/cases/{case_id}")
    assert resp.status_code == 200
    case_info = resp.json()
    assert "Apex Infrastructure" in case_info["title"]
    assert "Commercial" in case_info["category"]
    assert "Delhi" in case_info["jurisdiction"]
    assert len(case_info["parties"]) == 2

    # 3. Documents listing
    resp = client.get(f"/api/cases/{case_id}/documents")
    assert resp.status_code == 200
    docs = resp.json()
    assert len(docs) >= 6
    doc_filenames = [d["filename"] for d in docs]
    assert any("Agreement" in f for f in doc_filenames)
    assert any("Notice" in f for f in doc_filenames)
    
    # Ingest a new document to test real file upload and auto-extraction
    new_doc_bytes = (
        b"From: Apex Infrastructure Ltd.\n"
        b"To: Metro Rail Urban Development Corp.\n"
        b"Date: 25 November 2024\n"
        b"Subject: Formal claim for outstanding retention release of INR 2,40,00,000 under Clause 18.2.\n"
        b"Payment is overdue since 30 October 2024. Please disburse within 15 days."
    )
    resp = client.post(
        f"/api/cases/{case_id}/documents",
        files={"file": ("supplementary_claim.txt", new_doc_bytes, "text/plain")}
    )
    assert resp.status_code == 200
    new_doc = resp.json()
    assert new_doc["id"] is not None
    assert new_doc["filename"] == "supplementary_claim.txt"

    # 4. Extracted Facts listing and confirmation
    resp = client.get(f"/api/cases/{case_id}/facts")
    assert resp.status_code == 200
    facts = resp.json()
    assert len(facts) >= 6
    candidate_fact = next((f for f in facts if f["status"] == "candidate"), None)
    if candidate_fact:
        patch_resp = client.patch(
            f"/api/cases/{case_id}/facts/{candidate_fact['id']}/status",
            json={"status": "confirmed"}
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["status"] == "confirmed"

    # 5. Evidence Graph and Relationships
    resp = client.get(f"/api/cases/{case_id}/evidence/graph")
    assert resp.status_code == 200
    graph = resp.json()
    assert "nodes" in graph and "edges" in graph
    assert len(graph["nodes"]) >= 6
    assert len(graph["edges"]) >= 5

    # Create a manual evidence link
    link_payload = {
        "source_id": graph["nodes"][0]["id"],
        "target_id": graph["nodes"][1]["id"],
        "relation_type": "references",
        "explanation": "Cross-referenced in claim documentation",
        "is_confirmed": True
    }
    resp = client.post(f"/api/cases/{case_id}/evidence/relationships", json=link_payload)
    assert resp.status_code == 200
    assert resp.json()["relation_type"] == "references"

    # 6. Evidence Pathfinding Algorithms
    start_node = graph["nodes"][0]["id"]
    target_node = graph["nodes"][-1]["id"]
    
    for algo in ["bfs", "dfs", "ucs", "astar", "greedy"]:
        resp = client.post(
            f"/api/cases/{case_id}/evidence/pathfinding",
            json={
                "source_id": start_node,
                "target_id": target_node,
                "algorithm": algo
            }
        )
        assert resp.status_code == 200
        path_res = resp.json()
        assert "algorithm" in path_res
        assert "visited_count" in path_res
        assert "path" in path_res

    # 7. Intelligent Legal Search (BM25, TF-IDF, exact, phrase)
    # BM25
    resp = client.post(
        f"/api/cases/{case_id}/search",
        json={"query": "milestone", "method": "bm25"}
    )
    assert resp.status_code == 200
    bm25_res = resp.json()
    assert len(bm25_res) > 0
    assert "snippets" in bm25_res[0] and len(bm25_res[0]["snippets"]) > 0

    # TF-IDF
    resp = client.post(
        f"/api/cases/{case_id}/search",
        json={"query": "invoice retention payment", "method": "tfidf"}
    )
    assert resp.status_code == 200
    tfidf_res = resp.json()
    assert len(tfidf_res) > 0

    # Exact substring
    resp = client.post(
        f"/api/cases/{case_id}/search",
        json={"query": "2,50,000", "method": "exact"}
    )
    assert resp.status_code == 200
    exact_res = resp.json()
    assert len(exact_res) > 0

    # Phrase search
    resp = client.post(
        f"/api/cases/{case_id}/search",
        json={"query": "Milestone 3", "method": "phrase"}
    )
    assert resp.status_code == 200
    phrase_res = resp.json()
    assert len(phrase_res) > 0

    # 8. Timeline and Inconsistencies
    resp = client.get(f"/api/cases/{case_id}/timeline")
    assert resp.status_code == 200
    events = resp.json()
    assert len(events) >= 5

    resp = client.get(f"/api/cases/{case_id}/inconsistencies")
    assert resp.status_code == 200
    inconsistencies = resp.json()
    assert len(inconsistencies) >= 2
    inc = inconsistencies[0]

    # Resolve an inconsistency
    patch_inc = client.patch(
        f"/api/cases/{case_id}/inconsistencies/{inc['id']}/status",
        json={"status": "resolved"}
    )
    assert patch_inc.status_code == 200
    assert patch_inc.json()["status"] == "resolved"

    # 9. Knowledge Representation & Reasoning Engine
    # Forward Chaining
    resp = client.post(f"/api/cases/{case_id}/reasoning/forward")
    assert resp.status_code == 200
    fwd = resp.json()
    assert "Forward Chaining" in fwd.get("algorithm", "")
    assert "derived_facts" in fwd
    assert len(fwd["derived_facts"]) > 0

    # Backward Chaining
    resp = client.post(
        f"/api/cases/{case_id}/reasoning/backward",
        json={
            "goal_predicate": "defect_claim_barred",
            "goal_args": ["milestone_3"]
        }
    )
    assert resp.status_code == 200
    bwd = resp.json()
    assert "backward" in bwd.get("algorithm", "").lower()
    assert bwd.get("proven") is True
    assert len(bwd.get("evidence", [])) > 0

    # Test Backward Chaining with missing prerequisite
    resp_unproven = client.post(
        f"/api/cases/{case_id}/reasoning/backward",
        json={
            "goal_predicate": "criminal_fraud",
            "goal_args": ["metro_rail"]
        }
    )
    assert resp_unproven.status_code == 200
    bwd_unp = resp_unproven.json()
    assert bwd_unp.get("proven") is False
    assert len(bwd_unp.get("missing_prerequisites", [])) > 0

    # 10. Legal Arguments & Authorities
    resp = client.get(f"/api/cases/{case_id}/arguments")
    assert resp.status_code == 200
    args = resp.json()
    assert len(args) >= 2

    resp = client.get(f"/api/cases/{case_id}/authorities")
    assert resp.status_code == 200
    authorities = resp.json()
    assert len(authorities) >= 2

    # Add a custom argument
    arg_payload = {
        "issue_title": "Viaduct Segment A Completion Estoppel",
        "argument_text": "Respondent is estopped from denying completion of Viaduct Segment A following Joint Inspection",
        "supporting_evidence_ids": [args[0]["id"]],
        "assumptions": "Authority of signing engineer is binding",
        "counterarguments": "Respondent claims certificate was without prejudice",
        "status": "confirmed"
    }
    resp = client.post(f"/api/cases/{case_id}/arguments", json=arg_payload)
    assert resp.status_code == 200
    assert resp.json()["issue_title"] == arg_payload["issue_title"]

    # 11. Case Preparation Report Brief
    resp = client.get(f"/api/cases/{case_id}/report")
    assert resp.status_code == 200
    report = resp.json()
    md = report.get("markdown", "")
    assert len(md) > 0
    assert "LEXVIGIL AI — CASE PREPARATION REPORT" in md
    assert "Apex Infrastructure Ltd." in md
    assert "Extracted Facts & Findings" in md
    assert "Chronological Timeline" in md

    # 12. Interactive AI Algorithm Lab Endpoints
    # 12.1 General Search Lab
    resp = client.post(
        "/api/lab/search",
        json={
            "algorithm": "astar",
            "start_node": "A",
            "target_node": "G"
        }
    )
    assert resp.status_code == 200
    search_lab_res = resp.json()
    assert search_lab_res["path"] is not None
    assert search_lab_res["path"][0] == "A"
    assert search_lab_res["path"][-1] == "G"

    # 12.2 Game Search Lab (Alpha-Beta pruning)
    resp = client.post(
        "/api/lab/game",
        json={
            "algorithm": "alpha_beta",
            "depth": 3,
            "iterations": 20
        }
    )
    assert resp.status_code == 200
    game_res = resp.json()
    assert "optimal_value" in game_res
    assert "pruned_branches_count" in game_res

    # 12.3 Logic Truth Table
    resp = client.post(
        "/api/lab/logic",
        json={"mode": "truth_table", "variables": ["P", "Q"], "formulas": ["P and Q", "P implies Q"]}
    )
    assert resp.status_code == 200
    tt = resp.json()
    assert len(tt["rows"]) == 4

    # 12.4 Logic Resolution Prover
    resp = client.post(
        "/api/lab/logic",
        json={
            "mode": "resolution",
            "clauses": [["~Breach", "Damages"], ["Breach"]],
            "query": "Damages"
        }
    )
    assert resp.status_code == 200
    res_out = resp.json()
    assert res_out["proved"] is True

    # 12.5 FOL Unification
    resp = client.post(
        "/api/lab/logic",
        json={
            "mode": "unification",
            "expr1": "Obligation(?contract, ?party, INR_1250000)",
            "expr2": "Obligation(EPC_Contract_3B, Metro_Rail, ?amount)"
        }
    )
    assert resp.status_code == 200
    unify_res = resp.json()
    assert unify_res["unifiable"] is True
    assert "?party" in unify_res["substitution"]

    # 12.6 CSP Solver (hearing_schedule & event_timeline)
    resp = client.post(
        "/api/lab/csp",
        json={"problem_type": "hearing_schedule"}
    )
    assert resp.status_code == 200
    csp_res = resp.json()
    assert csp_res["solution"] is not None

    resp = client.post(
        "/api/lab/csp",
        json={"problem_type": "event_timeline"}
    )
    assert resp.status_code == 200
    csp_timeline = resp.json()
    assert csp_timeline["solution"] is not None

    # 12.7 Machine Learning: Classification
    resp = client.post("/api/lab/ml?mode=classification")
    assert resp.status_code == 200
    ml_res = resp.json()
    assert ml_res["accuracy"] >= 0.8
    assert "confusion_matrix" in ml_res

    # 12.8 Machine Learning: Clustering
    resp = client.post("/api/lab/ml?mode=clustering&k=3")
    assert resp.status_code == 200
    cluster_res = resp.json()
    assert len(cluster_res["final_centroids"]) == 3
    assert len(cluster_res["labeled_points"]) > 0

    # 12.9 Reinforcement Learning: Tabular Q-Learning
    resp = client.post(
        "/api/lab/rl",
        json={"episodes": 100, "alpha": 0.2, "gamma": 0.9, "epsilon": 0.3}
    )
    assert resp.status_code == 200
    rl_res = resp.json()
    assert rl_res["episodes"] == 100
    assert "optimal_policy" in rl_res
    assert len(rl_res["reward_progression"]) == 100

    # 13. Preserved Contract Review Functionality
    import time
    sample_resp = client.post("/api/contracts/sample")
    assert sample_resp.status_code in [200, 202]
    aid = sample_resp.json()["id"]
    deadline = time.monotonic() + 5
    res_obj = {}
    while time.monotonic() < deadline:
        get_analysis = client.get(f"/api/analyses/{aid}")
        assert get_analysis.status_code == 200
        res_obj = get_analysis.json()
        if res_obj.get("status") == "completed":
            break
        time.sleep(0.05)
    assert res_obj.get("status") == "completed"
    assert "result" in res_obj
