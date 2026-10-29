"""Comprehensive tests for Case Intelligence, Algorithms, Reasoning, and AI Lab."""
import pytest
from sqlalchemy import create_engine
from backend.cases import CaseManager
from backend.graph_algorithms import Graph, bfs, dfs, uniform_cost_search, greedy_best_first_search, astar_search, hill_climbing
from backend.search_engine import CaseSearchIndex
from backend.reasoning_engine import ReasoningEngine
from backend.logic_csp import generate_truth_table, propositional_resolution, fol_unify_demonstration, CSP, solve_csp_backtracking
from backend.ai_lab import minimax, alpha_beta_search, mcts_demonstration, expectiminimax, train_supervised_classifier, kmeans_clustering, run_q_learning
from backend.demo_case import load_fictional_demo_case


@pytest.fixture
def test_cm():
    engine = create_engine("sqlite:///:memory:")
    return CaseManager(engine)


def test_case_lifecycle(test_cm):
    owner_a = "user_alpha"
    owner_b = "user_beta"

    # Create Case
    case_a = test_cm.create_case(
        owner=owner_a,
        title="Acme Construction Dispute",
        reference="ARB/2024/001",
        category="Commercial",
        parties=["Acme Ltd.", "Beta Corp."],
        jurisdiction="Delhi",
        court="High Court"
    )
    assert case_a["title"] == "Acme Construction Dispute"
    assert case_a["doc_count"] == 0

    # Test Case Isolation
    assert test_cm.get_case(case_a["id"], owner_b) is None
    cases_b = test_cm.list_cases(owner_b)
    assert len(cases_b) == 0

    # Add document
    doc = test_cm.add_document(
        case_id=case_a["id"],
        owner=owner_a,
        filename="contract.txt",
        file_type="txt",
        file_size=120,
        text_content="Section 4.1 Payment obligation: The buyer shall pay INR 5000 within 30 days.",
        pages=[{"page": 1, "text": "Section 4.1 Payment obligation: The buyer shall pay INR 5000 within 30 days."}]
    )
    assert doc["filename"] == "contract.txt"

    # Add fact
    fact = test_cm.add_fact(
        case_id=case_a["id"],
        document_id=doc["id"],
        text_span="The buyer shall pay INR 5000",
        entity="Buyer",
        category="Obligation",
        fact_type="covenant",
        status="candidate"
    )
    assert fact["text"] == "The buyer shall pay INR 5000"

    # Update fact status
    ok = test_cm.update_fact_status(fact["id"], case_a["id"], "confirmed")
    assert ok is True
    updated_fact = test_cm.get_fact(fact["id"], case_a["id"])
    assert updated_fact["status"] == "confirmed"

    # Delete case cascades cleanly
    deleted = test_cm.delete_case(case_a["id"], owner_a)
    assert deleted is True
    assert test_cm.get_case(case_a["id"], owner_a) is None
    assert len(test_cm.list_documents(case_a["id"])) == 0
    assert len(test_cm.list_facts(case_a["id"])) == 0


def test_graph_search_algorithms():
    g = Graph(directed=False)
    # A - B - C - D with cycle A - C
    g.add_node("A", x=0, y=0)
    g.add_node("B", x=1, y=0)
    g.add_node("C", x=2, y=0)
    g.add_node("D", x=3, y=0)
    g.add_node("Isolated", x=10, y=10)

    g.add_edge("A", "B", weight=2.0)
    g.add_edge("B", "C", weight=3.0)
    g.add_edge("A", "C", weight=10.0)  # direct but expensive edge
    g.add_edge("C", "D", weight=1.0)

    # 1. BFS finds shortest hop path (A -> C -> D or A -> B -> C -> D)
    res_bfs = bfs(g, "A", "D")
    assert res_bfs["found"] is True
    assert res_bfs["path"][0] == "A"
    assert res_bfs["path"][-1] == "D"
    assert len(res_bfs["steps"]) > 0

    # 2. DFS
    res_dfs = dfs(g, "A", "D")
    assert res_dfs["found"] is True
    assert res_dfs["path"][0] == "A"
    assert res_dfs["path"][-1] == "D"

    # 3. UCS (Dijkstra) finds minimum cost path: A -> B -> C -> D (cost 2+3+1 = 6)
    res_ucs = uniform_cost_search(g, "A", "D")
    assert res_ucs["found"] is True
    assert res_ucs["path"] == ["A", "B", "C", "D"]
    assert res_ucs["path_cost"] == 6.0

    # 4. A* Search with Euclidean heuristic finds optimal path
    res_astar = astar_search(g, "A", "D")
    assert res_astar["found"] is True
    assert res_astar["path"] == ["A", "B", "C", "D"]
    assert res_astar["path_cost"] == 6.0

    # 5. Greedy Best-First Search
    res_greedy = greedy_best_first_search(g, "A", "D")
    assert res_greedy["found"] is True
    assert res_greedy["path"][-1] == "D"

    # 6. Unreachable target handling
    res_unreach = bfs(g, "A", "Isolated")
    assert res_unreach["found"] is False
    assert res_unreach["path"] == []

    # 7. Hill Climbing
    states = {"S1": 1.0, "S2": 3.0, "S3": 5.0, "S4": 4.0}
    adj = {"S1": ["S2"], "S2": ["S1", "S3"], "S3": ["S2", "S4"], "S4": ["S3"]}
    res_hc = hill_climbing(states, adj, "S1")
    assert res_hc["final_state"] == "S3"
    assert res_hc["final_value"] == 5.0


def test_intelligent_search_engine():
    idx = CaseSearchIndex()
    idx.add_document("doc1", "Services Agreement", "The contractor shall deliver milestone foundation works within thirty calendar days.")
    idx.add_document("doc2", "Tax Invoice", "Invoice #884 for foundation concrete pour amounting to INR 12,50,000.")
    idx.add_document("doc3", "Demand Notice", "Notice of default demanding payment of outstanding foundation debt.")

    # BM25 search
    res_bm25 = idx.search_bm25("foundation works")
    assert len(res_bm25) >= 2
    assert res_bm25[0]["doc_id"] == "doc1"
    assert "foundation" in res_bm25[0]["explanation"]

    # TF-IDF search
    res_tfidf = idx.search_tfidf("invoice concrete")
    assert len(res_tfidf) >= 1
    assert res_tfidf[0]["doc_id"] == "doc2"

    # Exact search
    res_exact = idx.search_exact("thirty calendar days")
    assert len(res_exact) == 1
    assert res_exact[0]["doc_id"] == "doc1"

    # Phrase search
    res_phrase = idx.search_phrase("milestone foundation")
    assert len(res_phrase) == 1
    assert res_phrase[0]["doc_id"] == "doc1"


def test_reasoning_forward_and_backward_chaining():
    engine = ReasoningEngine()
    # Facts
    engine.add_fact("contract_signed", ["apex", "metro_rail"], ["EV-01"])
    engine.add_fact("milestone_certified", ["milestone_3"], ["EV-02"])
    engine.add_fact("payment_withheld", ["metro_rail", "inr_2_50_000"], ["EV-03"])

    # Rule 1: milestone_certified(?m) -> payment_due(?m)
    engine.add_rule(
        "R1", "Certification Establishes Due",
        [{"predicate": "milestone_certified", "args": ["?m"]}],
        {"predicate": "payment_due", "args": ["?m"]}
    )

    # Rule 2: payment_due(?m) and payment_withheld(?party, ?amt) -> actionable_default(?party, ?amt)
    engine.add_rule(
        "R2", "Default on Withheld Certified Milestone",
        [
            {"predicate": "payment_due", "args": ["?m"]},
            {"predicate": "payment_withheld", "args": ["?p", "?amt"]}
        ],
        {"predicate": "actionable_default", "args": ["?p", "?amt"]}
    )

    # Run Forward Chaining
    fw_res = engine.forward_chain()
    assert fw_res["new_facts_derived"] == 2
    assert any("actionable_default(metro_rail, inr_2_50_000)" in f["representation"] for f in fw_res["derived_facts"])
    assert len(fw_res["inference_traces"]) == 2

    # Run Backward Chaining on proven goal
    bw_res = engine.backward_chain("actionable_default", ["metro_rail", "inr_2_50_000"])
    assert bw_res["proven"] is True
    assert "EV-02" in bw_res["evidence"]
    assert "EV-03" in bw_res["evidence"]

    # Run Backward Chaining on unproven goal
    bw_unproven = engine.backward_chain("criminal_fraud", ["metro_rail"])
    assert bw_unproven["proven"] is False
    assert len(bw_unproven["missing_prerequisites"]) > 0


def test_logic_and_csp():
    # 1. Truth Table
    tt = generate_truth_table(["P", "Q"], ["P and Q", "P implies Q"])
    assert len(tt["rows"]) == 4
    assert tt["summary"]["P implies Q"]["satisfiable"] is True

    # 2. Propositional Resolution Refutation
    # KB: ~P v Q (P implies Q), P. Query: Q.
    # Refutation adds ~Q. Resolution: (~P v Q) and P -> Q; Q and ~Q -> empty clause.
    res_kb = [["~P", "Q"], ["P"]]
    res = propositional_resolution(res_kb, "Q")
    assert res["proved"] is True
    assert any(s.get("contradiction") for s in res["steps"])

    # 3. First-Order Logic Unification
    unif = fol_unify_demonstration("Obligation(?x, Vendor, 5000)", "Obligation(ContractA, ?y, 5000)")
    assert unif["unifiable"] is True
    assert unif["substitution"]["?x"] == "ContractA"
    assert unif["substitution"]["?y"] == "Vendor"

    # 4. CSP Backtracking
    vars_list = ["Hearing1", "Hearing2", "Hearing3"]
    domains = {"Hearing1": [1, 2], "Hearing2": [1, 2], "Hearing3": [2, 3]}
    csp = CSP(vars_list, domains)
    csp.add_binary_constraint("Hearing1", "Hearing2", lambda h1, h2: h1 != h2, "Distinct time slots")
    csp.add_binary_constraint("Hearing2", "Hearing3", lambda h2, h3: h2 != h3, "Distinct time slots")
    sol = solve_csp_backtracking(csp)
    assert sol["solved"] is True
    assert sol["solution"]["Hearing1"] != sol["solution"]["Hearing2"]
    assert sol["solution"]["Hearing2"] != sol["solution"]["Hearing3"]


def test_ai_lab_components():
    # 1. Minimax & AlphaBeta
    tree = {
        "name": "Root", "type": "max",
        "children": [
            {"name": "M1", "type": "min", "children": [{"name": "A", "value": 3.0}, {"name": "B", "value": 5.0}]},
            {"name": "M2", "type": "min", "children": [{"name": "C", "value": 2.0}, {"name": "D", "value": 9.0}]}
        ]
    }
    mm_res = minimax(tree, depth=2, is_maximizing=True)
    assert mm_res["optimal_value"] == 3.0

    ab_res = alpha_beta_search(tree, depth=2, alpha=-float("inf"), beta=float("inf"), is_maximizing=True)
    assert ab_res["optimal_value"] == 3.0

    # 2. MCTS
    mcts_res = mcts_demonstration(iterations=25)
    assert mcts_res["recommended_action"] in ["Settle_Early", "File_Suit", "Mediate"]

    # 3. Expectiminimax
    tree_exp = {
        "name": "Root", "type": "max",
        "children": [
            {"name": "Sure_Option", "type": "leaf", "value": 40.0},
            {
                "name": "Chance_Option", "type": "chance",
                "children": [
                    {"name": "Win", "type": "leaf", "value": 100.0, "prob": 0.5},
                    {"name": "Lose", "type": "leaf", "value": 0.0, "prob": 0.5}
                ]
            }
        ]
    }
    exp_res = expectiminimax(tree_exp)
    assert exp_res["expected_value"] == 50.0

    # 4. Machine Learning: Naive Bayes
    ml_res = train_supervised_classifier()
    assert ml_res["accuracy"] >= 0.60
    assert "Contract" in ml_res["classes"]
    assert len(ml_res["per_class_metrics"]) == 4

    # 5. K-Means Clustering
    km_res = kmeans_clustering(k=3, max_iters=15)
    assert len(km_res["final_centroids"]) == 3
    assert len(km_res["labeled_points"]) == 12

    # 6. Tabular Q-Learning
    rl_res = run_q_learning(episodes=50)
    assert "Intake" in rl_res["optimal_policy"]
    assert len(rl_res["reward_progression"]) == 50


def test_fictional_demo_case_loading(test_cm):
    demo = load_fictional_demo_case(test_cm, "test_owner")
    assert demo["id"] == "DEMO-CASE-APEX-METRO-2024"
    assert demo["title"] == "Apex Infrastructure Ltd. v. Metro Rail Urban Development Corp."

    # Check documents
    docs = test_cm.list_documents(demo["id"])
    assert len(docs) == 6

    # Check facts
    facts = test_cm.list_facts(demo["id"])
    assert len(facts) >= 10

    # Check evidence & relationships
    ev = test_cm.list_evidence_items(demo["id"])
    assert len(ev) == 6
    rels = test_cm.list_evidence_relationships(demo["id"])
    assert len(rels) == 6

    # Check timeline
    timeline = test_cm.list_timeline_events(demo["id"])
    assert len(timeline) == 9

    # Check inconsistencies
    incons = test_cm.list_inconsistencies(demo["id"])
    assert len(incons) == 4

    # Check authorities & arguments
    args = test_cm.list_arguments(demo["id"])
    assert len(args) == 2
    auths = test_cm.list_authorities(demo["id"])
    assert len(auths) == 3
