"""Interactive AI Algorithm Lab: Game Search, Machine Learning, and Reinforcement Learning."""
import math
import random
from typing import Any, Dict, List, Optional, Tuple


# =====================================================================
# 1. GAME SEARCH: MINIMAX, ALPHA-BETA PRUNING, MCTS, EXPECTIMINIMAX
# =====================================================================

class GameTreeNode:
    def __init__(self, name: str, value: Optional[float] = None, children: Optional[List['GameTreeNode']] = None, node_type: str = "max"):
        self.name = name
        self.value = value
        self.children = children or []
        self.node_type = node_type  # "max", "min", "chance"


def minimax(node: Dict[str, Any], depth: int, is_maximizing: bool) -> Dict[str, Any]:
    """Classic Minimax game tree evaluation."""
    trace = []
    
    def _search(curr: Dict[str, Any], d: int, maximizing: bool) -> Tuple[float, List[Dict[str, Any]]]:
        children = curr.get("children", [])
        if d == 0 or not children:
            val = float(curr.get("value", 0.0))
            return val, [{"node": curr["name"], "eval": val, "depth": d, "action": f"Terminal/Leaf node '{curr['name']}' eval={val}"}]

        node_traces = []
        if maximizing:
            max_eval = -float("inf")
            best_child = None
            for child in children:
                val, child_trace = _search(child, d - 1, False)
                node_traces.extend(child_trace)
                if val > max_eval:
                    max_eval = val
                    best_child = child["name"]
            node_traces.append({
                "node": curr["name"],
                "eval": max_eval,
                "best_move": best_child,
                "depth": d,
                "action": f"MAX node '{curr['name']}' selected max value {max_eval} from child '{best_child}'"
            })
            return max_eval, node_traces
        else:
            min_eval = float("inf")
            best_child = None
            for child in children:
                val, child_trace = _search(child, d - 1, True)
                node_traces.extend(child_trace)
                if val < min_eval:
                    min_eval = val
                    best_child = child["name"]
            node_traces.append({
                "node": curr["name"],
                "eval": min_eval,
                "best_move": best_child,
                "depth": d,
                "action": f"MIN node '{curr['name']}' selected min value {min_eval} from child '{best_child}'"
            })
            return min_eval, node_traces

    opt_val, search_steps = _search(node, depth, is_maximizing)
    return {
        "algorithm": "Minimax",
        "optimal_value": opt_val,
        "steps": search_steps,
        "total_steps": len(search_steps)
    }


def _format_bound(val: float) -> Any:
    if val == float("inf"):
        return "+∞"
    if val == -float("inf"):
        return "-∞"
    return round(val, 2)


def alpha_beta_search(node: Dict[str, Any], depth: int, alpha: float, beta: float, is_maximizing: bool) -> Dict[str, Any]:
    """Minimax with Alpha-Beta Pruning and pruned branch counter."""
    pruned_count = 0
    search_steps = []

    def _ab(curr: Dict[str, Any], d: int, a: float, b: float, maximizing: bool) -> float:
        nonlocal pruned_count
        children = curr.get("children", [])
        if d == 0 or not children:
            val = float(curr.get("value", 0.0))
            search_steps.append({
                "node": curr["name"],
                "eval": val,
                "alpha": _format_bound(a),
                "beta": _format_bound(b),
                "action": f"Leaf '{curr['name']}' evaluated at {val}"
            })
            return val

        if maximizing:
            v = -float("inf")
            best_child = None
            for idx, child in enumerate(children):
                val = _ab(child, d - 1, a, b, False)
                if val > v:
                    v = val
                    best_child = child["name"]
                a = max(a, v)
                if b <= a:
                    pruned = len(children) - (idx + 1)
                    pruned_count += pruned
                    search_steps.append({
                        "node": curr["name"],
                        "eval": v,
                        "alpha": _format_bound(a),
                        "beta": _format_bound(b),
                        "pruned_branches": pruned,
                        "action": f"PRUNED {pruned} remaining child branches at MAX node '{curr['name']}' because beta ({_format_bound(b)}) <= alpha ({_format_bound(a)})"
                    })
                    break
            search_steps.append({
                "node": curr["name"],
                "eval": v,
                "best_move": best_child,
                "alpha": _format_bound(a),
                "beta": _format_bound(b),
                "action": f"MAX node '{curr['name']}' evaluated to {v}"
            })
            return v
        else:
            v = float("inf")
            best_child = None
            for idx, child in enumerate(children):
                val = _ab(child, d - 1, a, b, True)
                if val < v:
                    v = val
                    best_child = child["name"]
                b = min(b, v)
                if b <= a:
                    pruned = len(children) - (idx + 1)
                    pruned_count += pruned
                    search_steps.append({
                        "node": curr["name"],
                        "eval": v,
                        "alpha": _format_bound(a),
                        "beta": _format_bound(b),
                        "pruned_branches": pruned,
                        "action": f"PRUNED {pruned} remaining child branches at MIN node '{curr['name']}' because beta ({_format_bound(b)}) <= alpha ({_format_bound(a)})"
                    })
                    break
            search_steps.append({
                "node": curr["name"],
                "eval": v,
                "best_move": best_child,
                "alpha": _format_bound(a),
                "beta": _format_bound(b),
                "action": f"MIN node '{curr['name']}' evaluated to {v}"
            })
            return v

    opt_val = _ab(node, depth, alpha, beta, is_maximizing)
    return {
        "algorithm": "Alpha-Beta Pruning",
        "optimal_value": opt_val,
        "pruned_branches_count": pruned_count,
        "steps": search_steps,
        "total_evaluations": len(search_steps)
    }


def mcts_demonstration(iterations: int = 40, exploration_constant: float = 1.414) -> Dict[str, Any]:
    """Monte Carlo Tree Search (Selection, Expansion, Rollout, Backpropagation) with UCB1."""
    random.seed(42)
    # Simple legal litigation game tree: Root -> [Negotiate, Sue, Mediate] -> ...
    actions = ["Settle_Early", "File_Suit", "Mediate"]
    tree = {
        "name": "Case_Decision_Root",
        "visits": 0,
        "wins": 0.0,
        "children": [
            {"name": a, "visits": 0, "wins": 0.0, "p_win": 0.55 if a == "Settle_Early" else 0.70 if a == "File_Suit" else 0.45}
            for a in actions
        ]
    }
    steps = []

    for it in range(1, iterations + 1):
        # 1. Selection using UCB1
        best_child = None
        best_ucb = -float("inf")
        for child in tree["children"]:
            if child["visits"] == 0:
                best_child = child
                break
            q = child["wins"] / child["visits"]
            u = exploration_constant * math.sqrt(math.log(tree["visits"]) / child["visits"])
            ucb = q + u
            if ucb > best_ucb:
                best_ucb = ucb
                best_child = child

        # 2. Simulation / Rollout
        sim_win = 1.0 if random.random() < best_child["p_win"] else 0.0

        # 3. Backpropagation
        best_child["visits"] += 1
        best_child["wins"] += sim_win
        tree["visits"] += 1
        tree["wins"] += sim_win

        steps.append({
            "iteration": it,
            "selected_action": best_child["name"],
            "simulation_result": "Win / Positive Settlement" if sim_win > 0 else "Loss / Adverse Costs",
            "child_visits": best_child["visits"],
            "child_win_rate": round(best_child["wins"] / best_child["visits"], 3),
            "root_visits": tree["visits"]
        })

    # Pick recommended action
    recommended = max(tree["children"], key=lambda c: c["visits"])
    return {
        "algorithm": "Monte Carlo Tree Search (MCTS)",
        "iterations": iterations,
        "tree_stats": [
            {
                "action": c["name"],
                "visits": c["visits"],
                "win_rate": round(c["wins"] / c["visits"], 3) if c["visits"] > 0 else 0.0
            }
            for c in tree["children"]
        ],
        "recommended_action": recommended["name"],
        "recommended_win_rate": round(recommended["wins"] / recommended["visits"], 3),
        "steps": steps[:25]  # Sample first 25 steps for display
    }


def expectiminimax(node: Dict[str, Any]) -> Dict[str, Any]:
    """Expectiminimax game search with chance (probabilistic) nodes."""
    steps = []

    def _eval(curr: Dict[str, Any]) -> float:
        ntype = curr.get("type", "leaf")
        name = curr.get("name", "node")
        if ntype == "leaf":
            v = float(curr.get("value", 0.0))
            steps.append({"node": name, "type": "leaf", "value": v, "action": f"Outcome '{name}' = {v}"})
            return v
        elif ntype == "max":
            best = -float("inf")
            for c in curr.get("children", []):
                val = _eval(c)
                best = max(best, val)
            steps.append({"node": name, "type": "max", "value": best, "action": f"MAX player chooses best value {best}"})
            return best
        elif ntype == "chance":
            expected = 0.0
            for c in curr.get("children", []):
                prob = float(c.get("prob", 1.0))
                val = _eval(c)
                expected += prob * val
            steps.append({"node": name, "type": "chance", "value": round(expected, 2), "action": f"CHANCE node computes expected value = {round(expected, 2)}"})
            return expected
        return 0.0

    result = _eval(node)
    return {
        "algorithm": "Expectiminimax Search",
        "expected_value": round(result, 2),
        "steps": steps
    }


# =====================================================================
# 2. MACHINE LEARNING: SUPERVISED CLASSIFICATION & K-MEANS CLUSTERING
# =====================================================================

def train_supervised_classifier() -> Dict[str, Any]:
    """Local transparent Naive Bayes text classifier for legal document types."""
    # Synthetic dataset of 24 representative legal document text snippets
    dataset = [
        # Contracts (0)
        ("Master services agreement governing performance and mutual obligations of buyer and vendor", "Contract"),
        ("The contractor agrees to provide technical consultancy services as defined in section 4", "Contract"),
        ("Non-disclosure and confidentiality terms binding receiving party for three calendar years", "Contract"),
        ("Commercial lease agreement specifying monthly rental sum and escalation clause", "Contract"),
        ("Employment contract with non-compete covenants and statutory severance entitlements", "Contract"),
        ("Software licensing agreement with terms of performance and covenants", "Contract"),
        # Invoices / Financials (1)
        ("Tax invoice for progress payment milestone two payable within thirty days", "Invoice"),
        ("Commercial debit note requesting immediate clearance of outstanding invoice amount", "Invoice"),
        ("Bank remittance receipt confirming partial wire transfer against bill reference", "Invoice"),
        ("Proforma invoice for machinery procurement with GST breakdown and bank details", "Invoice"),
        ("Payment advice note acknowledging receipt of partial payment for civil works", "Invoice"),
        ("Billing invoice summary reflecting overdue interest charges on unpaid invoices", "Invoice"),
        # Court Pleadings / Claims (2)
        ("Plaint filed under commercial courts act praying for decree of damages and interest", "Pleading"),
        ("Written statement of defendant denying allegations of breach of contract and liability", "Pleading"),
        ("Affidavit in support of interim application for preservation of subject property", "Pleading"),
        ("Statement of claim before learned arbitral tribunal seeking liquidated damages", "Pleading"),
        ("Counterclaim filed by respondent alleging delayed delivery and defective materials", "Pleading"),
        ("Plaint application seeking stay on execution proceedings in civil suit", "Pleading"),
        # Statutory Notices (3)
        ("Legal demand notice under section 138 of negotiable instruments act for bounced cheque", "Statutory_Notice"),
        ("Notice of default under section 73 of indian contract act demanding cure of breach", "Statutory_Notice"),
        ("Statutory winding up notice demanding payment of admitted operational debt within 21 days", "Statutory_Notice"),
        ("Legal notice invoking arbitration clause and nominating sole arbitrator", "Statutory_Notice"),
        ("Show cause notice issued by regulatory authority for non-compliance with rules", "Statutory_Notice"),
        ("Statutory notice demanding immediate cure of breach under section 80", "Statutory_Notice")
    ]

    # Stratified train/test split (5 train, 1 test per class)
    classes = sorted(list(set(label for _, label in dataset)))
    by_class = {c: [item for item in dataset if item[1] == c] for c in classes}
    train_data = []
    test_data = []
    for c in classes:
        train_data.extend(by_class[c][:5])
        test_data.extend(by_class[c][5:])

    # Build Vocabulary & Class priors
    class_word_counts = {c: {} for c in classes}
    class_total_words = {c: 0 for c in classes}
    class_doc_counts = {c: 0 for c in classes}
    vocab = set()

    for text, label in train_data:
        class_doc_counts[label] += 1
        tokens = [t.lower() for t in text.split() if len(t) > 2]
        for t in tokens:
            vocab.add(t)
            class_word_counts[label][t] = class_word_counts[label].get(t, 0) + 1
            class_total_words[label] += 1

    V = len(vocab)
    total_train_docs = len(train_data)

    def predict(text_input: str) -> Tuple[str, Dict[str, float]]:
        tokens = [t.lower() for t in text_input.split() if len(t) > 2]
        scores = {}
        for c in classes:
            # log prior
            log_prob = math.log(class_doc_counts[c] / total_train_docs)
            for t in tokens:
                if t in vocab:
                    # Laplace smoothing
                    count = class_word_counts[c].get(t, 0) + 1
                    denom = class_total_words[c] + V
                    log_prob += math.log(count / denom)
            scores[c] = log_prob
        # Softmax normalize scores for readability
        max_s = max(scores.values())
        exp_scores = {c: math.exp(scores[c] - max_s) for c in classes}
        total_exp = sum(exp_scores.values())
        probs = {c: round(exp_scores[c] / total_exp, 3) for c in classes}
        best_c = max(probs, key=probs.get)
        return best_c, probs

    # Evaluate on test set
    confusion = {c1: {c2: 0 for c2 in classes} for c1 in classes}
    test_evaluations = []
    correct = 0

    for text, actual in test_data:
        pred, probs = predict(text)
        confusion[actual][pred] += 1
        if pred == actual:
            correct += 1
        test_evaluations.append({
            "text": text,
            "actual_class": actual,
            "predicted_class": pred,
            "correct": pred == actual,
            "class_probabilities": probs
        })

    accuracy = correct / len(test_data) if test_data else 0.0

    # Precision, Recall, F1 per class
    metrics_per_class = {}
    for c in classes:
        tp = confusion[c][c]
        fp = sum(confusion[other][c] for other in classes if other != c)
        fn = sum(confusion[c][other] for other in classes if other != c)
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
        metrics_per_class[c] = {
            "precision": round(prec, 3),
            "recall": round(rec, 3),
            "f1_score": round(f1, 3),
            "true_positives": tp,
            "support": tp + fn
        }

    macro_f1 = sum(m["f1_score"] for m in metrics_per_class.values()) / len(classes)

    return {
        "algorithm": "Multinomial Naive Bayes Legal Document Classifier",
        "dataset_size": len(dataset),
        "train_samples": len(train_data),
        "test_samples": len(test_data),
        "vocabulary_size": V,
        "classes": classes,
        "accuracy": round(accuracy, 3),
        "macro_f1": round(macro_f1, 3),
        "per_class_metrics": metrics_per_class,
        "confusion_matrix": confusion,
        "test_predictions": test_evaluations
    }


def kmeans_clustering(k: int = 3, max_iters: int = 20) -> Dict[str, Any]:
    """K-Means clustering on legal dispute cases by claim value and duration."""
    random.seed(42)
    # Synthetic cases: (Claim Value in Lakhs, Duration in Months, Case Name)
    data_points = [
        {"name": "Summary Debt Claim A", "x": 12.0, "y": 4.0},
        {"name": "Summary Debt Claim B", "x": 18.0, "y": 6.0},
        {"name": "Vendor Invoice Default", "x": 15.0, "y": 5.0},
        {"name": "Small Works Payment", "x": 22.0, "y": 8.0},
        {"name": "Commercial Lease Breach", "x": 85.0, "y": 24.0},
        {"name": "Supply Contract Dispute", "x": 110.0, "y": 30.0},
        {"name": "Franchise Royalty Claim", "x": 95.0, "y": 28.0},
        {"name": "IP Licensing Dispute", "x": 125.0, "y": 36.0},
        {"name": "Major Infrastructure EPC", "x": 450.0, "y": 60.0},
        {"name": "Metro Rail Consortium", "x": 520.0, "y": 68.0},
        {"name": "Port Concession Arbitration", "x": 600.0, "y": 72.0},
        {"name": "Highway EPC Delay Claim", "x": 480.0, "y": 58.0}
    ]

    # Initialize centroids randomly from points
    centroids = [{"x": p["x"], "y": p["y"]} for p in random.sample(data_points, k)]
    steps = []

    for it in range(1, max_iters + 1):
        # 1. Assignment step
        clusters: List[List[Dict[str, Any]]] = [[] for _ in range(k)]
        for p in data_points:
            dists = [math.sqrt((p["x"] - c["x"]) ** 2 + (p["y"] - c["y"]) ** 2) for c in centroids]
            best_idx = int(dists.index(min(dists)))
            clusters[best_idx].append(p)

        # 2. Update step
        new_centroids = []
        max_shift = 0.0
        for i in range(k):
            pts = clusters[i]
            if pts:
                new_x = sum(p["x"] for p in pts) / len(pts)
                new_y = sum(p["y"] for p in pts) / len(pts)
            else:
                new_x, new_y = centroids[i]["x"], centroids[i]["y"]
            shift = math.sqrt((new_x - centroids[i]["x"]) ** 2 + (new_y - centroids[i]["y"]) ** 2)
            max_shift = max(max_shift, shift)
            new_centroids.append({"x": round(new_x, 2), "y": round(new_y, 2)})

        steps.append({
            "iteration": it,
            "centroids": [{"x": round(c["x"], 2), "y": round(c["y"], 2)} for c in centroids],
            "cluster_sizes": [len(c) for c in clusters],
            "max_centroid_shift": round(max_shift, 3)
        })

        centroids = new_centroids
        if max_shift < 0.01:
            break

    # Calculate Inertia (Sum of squared distances to centroid)
    inertia = 0.0
    labeled_points = []
    for i, pts in enumerate(clusters):
        c = centroids[i]
        for p in pts:
            dist_sq = (p["x"] - c["x"]) ** 2 + (p["y"] - c["y"]) ** 2
            inertia += dist_sq
            labeled_points.append({
                "name": p["name"],
                "claim_value_lakhs": p["x"],
                "duration_months": p["y"],
                "assigned_cluster": i,
                "cluster_label": "Low-value Quick Recovery" if i == 0 else "Mid-tier Commercial" if i == 1 else "High-stakes Infrastructure/Arbitration"
            })

    return {
        "algorithm": "K-Means Dispute Profile Clustering",
        "k": k,
        "iterations_to_converge": len(steps),
        "inertia": round(inertia, 2),
        "final_centroids": centroids,
        "labeled_points": labeled_points,
        "convergence_steps": steps
    }


# =====================================================================
# 3. REINFORCEMENT LEARNING: TABULAR Q-LEARNING
# =====================================================================

def run_q_learning(episodes: int = 150, alpha: float = 0.2, gamma: float = 0.9, epsilon: float = 0.3) -> Dict[str, Any]:
    """Tabular Q-Learning agent learning litigation dispute resolution strategy."""
    random.seed(42)
    # 5 Litigation States:
    # S0: Intake & Demand Notice
    # S1: Informal Settlement Negotiations
    # S2: Arbitration / Filing Plaint
    # S3: Evidence & Cross-Examination
    # S4: Award / Decree Enforcement (Goal State)
    # S5: Abandoned / Procedural Dismissal (Penalty State)
    
    states = ["Intake", "Negotiation", "Litigation", "Trial", "Enforcement", "Dismissal"]
    actions = ["Settle", "Litigate_Aggressive", "Procedural_Delay", "Compromise"]

    # Initialize Q-table with zeros
    q_table = {s: {a: 0.0 for a in actions} for s in states}

    def step_env(s: str, a: str) -> Tuple[str, float, bool]:
        if s == "Intake":
            if a == "Settle":
                return "Negotiation", 5.0, False
            elif a == "Litigate_Aggressive":
                return "Litigation", -2.0, False
            elif a == "Procedural_Delay":
                return "Dismissal", -20.0, True
            else:
                return "Negotiation", 2.0, False

        elif s == "Negotiation":
            if a == "Settle" or a == "Compromise":
                return "Enforcement", 40.0, True  # Successful settlement!
            elif a == "Litigate_Aggressive":
                return "Trial", -5.0, False
            else:
                return "Litigation", -1.0, False

        elif s == "Litigation":
            if a == "Litigate_Aggressive":
                return "Trial", 10.0, False
            elif a == "Settle":
                return "Enforcement", 30.0, True
            elif a == "Procedural_Delay":
                return "Dismissal", -30.0, True
            else:
                return "Trial", 5.0, False

        elif s == "Trial":
            if a == "Litigate_Aggressive" or a == "Compromise":
                return "Enforcement", 60.0, True  # Win at trial
            else:
                return "Dismissal", -40.0, True

        return s, 0.0, True

    reward_history = []
    step_history = []

    for ep in range(1, episodes + 1):
        curr_state = "Intake"
        total_ep_reward = 0.0
        steps_count = 0

        while curr_state not in ("Enforcement", "Dismissal") and steps_count < 20:
            steps_count += 1
            # Epsilon-greedy action selection
            if random.random() < epsilon:
                action = random.choice(actions)
            else:
                best_val = max(q_table[curr_state].values())
                best_actions = [a for a in actions if q_table[curr_state][a] == best_val]
                action = random.choice(best_actions)

            nxt_state, reward, done = step_env(curr_state, action)
            total_ep_reward += reward

            # Q-learning update: Q(s, a) = Q(s, a) + alpha * (r + gamma * max Q(s', a') - Q(s, a))
            next_max_q = max(q_table[nxt_state].values()) if not done else 0.0
            old_q = q_table[curr_state][action]
            q_table[curr_state][action] = old_q + alpha * (reward + gamma * next_max_q - old_q)

            curr_state = nxt_state
            if done:
                break

        reward_history.append(round(total_ep_reward, 2))
        step_history.append(steps_count)

    # Derive optimal policy
    optimal_policy = {}
    for s in ["Intake", "Negotiation", "Litigation", "Trial"]:
        best_a = max(q_table[s], key=q_table[s].get)
        optimal_policy[s] = {
            "recommended_action": best_a,
            "q_value": round(q_table[s][best_a], 2)
        }

    return {
        "algorithm": "Tabular Q-Learning (Litigation Policy Optimization)",
        "episodes": episodes,
        "alpha": alpha,
        "gamma": gamma,
        "epsilon": epsilon,
        "states": states,
        "actions": actions,
        "q_table": {s: {a: round(v, 2) for a, v in q_table[s].items()} for s in states},
        "optimal_policy": optimal_policy,
        "reward_progression": reward_history,
        "average_final_reward": round(sum(reward_history[-20:]) / 20, 2) if len(reward_history) >= 20 else round(sum(reward_history) / len(reward_history), 2),
        "explanation": "Q-learning successfully converges to the optimal litigation strategy maximizing recovery while avoiding procedural dismissal."
    }
