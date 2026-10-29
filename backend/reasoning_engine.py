"""Explainable knowledge representation and reasoning engine with forward and backward chaining."""
from typing import Any, Dict, List, Optional, Set, Tuple


class Fact:
    def __init__(self, predicate: str, args: List[Any], evidence_ids: Optional[List[str]] = None, source: str = "direct"):
        self.predicate = predicate.strip().lower()
        self.args = [str(a).strip().lower() for a in args]
        self.evidence_ids = evidence_ids or []
        self.source = source  # "direct", "inferred", "allegation"

    def key(self) -> str:
        return f"{self.predicate}({', '.join(self.args)})"

    def matches(self, pattern_predicate: str, pattern_args: List[str], bindings: Dict[str, str]) -> Optional[Dict[str, str]]:
        if self.predicate != pattern_predicate.strip().lower():
            return None
        if len(self.args) != len(pattern_args):
            return None
        new_bindings = dict(bindings)
        for actual, pat in zip(self.args, pattern_args):
            pat = pat.strip()
            if pat.startswith("?"):  # Variable
                if pat in new_bindings:
                    if new_bindings[pat] != actual:
                        return None
                else:
                    new_bindings[pat] = actual
            else:  # Constant
                if pat.lower() != actual:
                    return None
        return new_bindings

    def to_dict(self) -> Dict[str, Any]:
        return {
            "predicate": self.predicate,
            "args": self.args,
            "representation": self.key(),
            "evidence_ids": self.evidence_ids,
            "source": self.source
        }


class Rule:
    def __init__(self, rule_id: str, name: str, premises: List[Dict[str, Any]], conclusion: Dict[str, Any], description: str = ""):
        self.rule_id = rule_id
        self.name = name
        self.premises = premises  # List of {"predicate": "...", "args": ["?x", "..."]}
        self.conclusion = conclusion  # {"predicate": "...", "args": ["?x", "..."]}
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.rule_id,
            "name": self.name,
            "premises": self.premises,
            "conclusion": self.conclusion,
            "description": self.description
        }


class ReasoningEngine:
    """Inference engine supporting forward chaining, backward chaining, and missing premise detection."""
    def __init__(self):
        self.facts: Dict[str, Fact] = {}
        self.rules: List[Rule] = []

    def add_fact(self, predicate: str, args: List[Any], evidence_ids: Optional[List[str]] = None, source: str = "direct") -> Fact:
        fact = Fact(predicate, args, evidence_ids, source)
        self.facts[fact.key()] = fact
        return fact

    def add_rule(self, rule_id: str, name: str, premises: List[Dict[str, Any]], conclusion: Dict[str, Any], description: str = "") -> Rule:
        rule = Rule(rule_id, name, premises, conclusion, description)
        self.rules.append(rule)
        return rule

    def forward_chain(self, max_iterations: int = 50) -> Dict[str, Any]:
        """Forward-chaining inference to derive all supported facts with complete deduction traces."""
        inferred_facts: List[Dict[str, Any]] = []
        traces: List[Dict[str, Any]] = []
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            new_facts_this_round = 0

            for rule in self.rules:
                # Find all satisfying variable bindings for rule premises
                bindings_list = [dict()]
                for premise in rule.premises:
                    p_pred = premise["predicate"]
                    p_args = premise["args"]
                    next_bindings = []
                    for b in bindings_list:
                        for f in self.facts.values():
                            matched_b = f.matches(p_pred, p_args, b)
                            if matched_b is not None:
                                next_bindings.append(matched_b)
                    bindings_list = next_bindings
                    if not bindings_list:
                        break

                for b in bindings_list:
                    # Construct candidate conclusion
                    c_pred = rule.conclusion["predicate"]
                    c_args = [b.get(a, a) for a in rule.conclusion["args"]]
                    cand_key = f"{c_pred.lower()}({', '.join([str(a).lower() for a in c_args])})"

                    if cand_key not in self.facts:
                        # Collect evidence from supporting premises
                        sup_evidence = []
                        sup_premises = []
                        for p in rule.premises:
                            p_pred = p["predicate"]
                            p_args = [b.get(a, a) for a in p["args"]]
                            matched_fact = next((f for f in self.facts.values() if f.predicate == p_pred.lower() and f.args == [str(x).lower() for x in p_args]), None)
                            if matched_fact:
                                sup_evidence.extend(matched_fact.evidence_ids)
                                sup_premises.append(matched_fact.key())

                        new_fact = Fact(c_pred, c_args, list(dict.fromkeys(sup_evidence)), source=f"rule:{rule.rule_id}")
                        self.facts[cand_key] = new_fact
                        new_facts_this_round += 1

                        trace_entry = {
                            "iteration": iteration,
                            "rule_id": rule.rule_id,
                            "rule_name": rule.name,
                            "bindings": b,
                            "premises_used": sup_premises,
                            "derived_conclusion": cand_key,
                            "evidence": list(dict.fromkeys(sup_evidence))
                        }
                        traces.append(trace_entry)
                        inferred_facts.append(new_fact.to_dict())

            if new_facts_this_round == 0:
                break

        return {
            "algorithm": "Forward Chaining Deduction",
            "total_facts": len(self.facts),
            "new_facts_derived": len(inferred_facts),
            "derived_facts": inferred_facts,
            "inference_traces": traces,
            "all_facts": [f.to_dict() for f in self.facts.values()],
            "limitations": [
                "Rule evaluation operates under a closed-world assumption relative to case inputs.",
                "Inferred findings depend on supplied premises and do not constitute legal adjudications."
            ]
        }

    def backward_chain(self, goal_predicate: str, goal_args: List[str]) -> Dict[str, Any]:
        """Backward-chaining goal-directed proof search with missing prerequisite detection."""
        goal_pred_clean = goal_predicate.strip().lower()
        goal_args_clean = [str(a).strip().lower() for a in goal_args]
        goal_key = f"{goal_pred_clean}({', '.join(goal_args_clean)})"

        proof_tree: List[Dict[str, Any]] = []
        missing_prerequisites: List[Dict[str, Any]] = []

        def prove(pred: str, args: List[str], bindings: Dict[str, str], depth: int = 0) -> Tuple[bool, List[str]]:
            if depth > 10:
                return False, []

            # 1. Check if fact already exists
            for f in self.facts.values():
                b = f.matches(pred, args, bindings)
                if b is not None:
                    proof_tree.append({
                        "depth": depth,
                        "goal": f"{pred}({', '.join(args)})",
                        "status": "PROVED_BY_KNOWN_FACT",
                        "fact": f.key(),
                        "evidence": f.evidence_ids
                    })
                    return True, f.evidence_ids

            # 2. Check rules that conclude this predicate
            rules_matching = [r for r in self.rules if r.conclusion["predicate"].lower() == pred.lower() and len(r.conclusion["args"]) == len(args)]
            
            if not rules_matching:
                missing_prerequisites.append({
                    "predicate": pred,
                    "args": args,
                    "reason": "No known fact or rule can establish this premise."
                })
                proof_tree.append({
                    "depth": depth,
                    "goal": f"{pred}({', '.join(args)})",
                    "status": "UNRESOLVED_NO_RULES"
                })
                return False, []

            for r in rules_matching:
                rule_bindings = dict(bindings)
                # Unify goal args with rule conclusion args
                unify_ok = True
                for g_arg, r_arg in zip(args, r.conclusion["args"]):
                    if r_arg.startswith("?"):
                        rule_bindings[r_arg] = g_arg
                    elif r_arg.lower() != g_arg.lower():
                        unify_ok = False
                        break
                if not unify_ok:
                    continue

                all_premises_proved = True
                rule_evidence = []
                for premise in r.premises:
                    p_args_bound = [rule_bindings.get(a, a) for a in premise["args"]]
                    ok, ev = prove(premise["predicate"], p_args_bound, rule_bindings, depth + 1)
                    if not ok:
                        all_premises_proved = False
                        missing_prerequisites.append({
                            "predicate": premise["predicate"],
                            "args": p_args_bound,
                            "required_by_rule": r.name,
                            "reason": "Prerequisite premise could not be proven."
                        })
                        break
                    rule_evidence.extend(ev)

                if all_premises_proved:
                    proof_tree.append({
                        "depth": depth,
                        "goal": f"{pred}({', '.join(args)})",
                        "status": f"PROVED_BY_RULE:{r.rule_id}",
                        "rule_name": r.name,
                        "evidence": list(dict.fromkeys(rule_evidence))
                    })
                    return True, list(dict.fromkeys(rule_evidence))

            return False, []

        is_proven, evidence = prove(goal_pred_clean, goal_args_clean, {})

        return {
            "algorithm": "Backward Chaining Goal Proof",
            "goal": goal_key,
            "proven": is_proven,
            "evidence": evidence,
            "proof_tree": proof_tree,
            "missing_prerequisites": missing_prerequisites,
            "limitations": [
                "Unproven goals indicate missing evidence or premises in the case record.",
                "Absence of proof is not proof of absence under common legal doctrine."
            ]
        }

    def check_contradictions(self) -> List[Dict[str, Any]]:
        """Identify logical inconsistencies between mutually exclusive facts."""
        contradictions = []
        fact_items = list(self.facts.values())

        for i, f1 in enumerate(fact_items):
            for f2 in fact_items[i + 1:]:
                # Discrepancy 1: Same event/transaction, different amounts
                if f1.predicate == f2.predicate and f1.predicate in ("payment_amount", "amount_due", "invoice_total"):
                    if len(f1.args) >= 2 and len(f2.args) >= 2 and f1.args[0] == f2.args[0] and f1.args[1] != f2.args[1]:
                        contradictions.append({
                            "issue_type": "Amount Discrepancy",
                            "severity": "HIGH",
                            "fact_a": f1.key(),
                            "fact_b": f2.key(),
                            "explanation": f"Record '{f1.args[0]}' reports amount '{f1.args[1]}' in one place and '{f2.args[1]}' in another.",
                            "evidence_a": f1.evidence_ids,
                            "evidence_b": f2.evidence_ids
                        })

                # Discrepancy 2: Conflicting dates for the same notice or delivery
                if f1.predicate == f2.predicate and f1.predicate in ("event_date", "notice_served_on", "completion_date"):
                    if len(f1.args) >= 2 and len(f2.args) >= 2 and f1.args[0] == f2.args[0] and f1.args[1] != f2.args[1]:
                        contradictions.append({
                            "issue_type": "Date Inconsistency",
                            "severity": "HIGH",
                            "fact_a": f1.key(),
                            "fact_b": f2.key(),
                            "explanation": f"Conflicting dates recorded for '{f1.args[0]}': '{f1.args[1]}' vs '{f2.args[1]}'.",
                            "evidence_a": f1.evidence_ids,
                            "evidence_b": f2.evidence_ids
                        })

                # Discrepancy 3: Active obligation vs Breach claim
                if (f1.predicate == "obligation_performed" and f2.predicate == "alleged_breach" and f1.args == f2.args) or \
                   (f2.predicate == "obligation_performed" and f1.predicate == "alleged_breach" and f1.args == f2.args):
                    contradictions.append({
                        "issue_type": "Performance vs Breach Conflict",
                        "severity": "MEDIUM",
                        "fact_a": f1.key(),
                        "fact_b": f2.key(),
                        "explanation": f"One record asserts performance of '{f1.args[0]}' while another asserts breach.",
                        "evidence_a": f1.evidence_ids,
                        "evidence_b": f2.evidence_ids
                    })

        return contradictions
