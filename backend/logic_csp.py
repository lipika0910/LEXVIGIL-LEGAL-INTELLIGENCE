"""Logic theorem-proving laboratory and Constraint Satisfaction Problem (CSP) engine."""
import itertools
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


# =====================================================================
# 1. PROPOSITIONAL LOGIC, TRUTH TABLES, AND RESOLUTION REFUTATION
# =====================================================================

def evaluate_prop_expr(expr: str, model: Dict[str, bool]) -> bool:
    """Evaluates a propositional expression with operators: not, and, or, implies, iff."""
    s = expr
    # Sort variables by length descending to avoid prefix replacement issues
    for var in sorted(model.keys(), key=len, reverse=True):
        val = "True" if model[var] else "False"
        s = re_sub_word(var, val, s)

    # Replace logical operators with python equivalents
    s = re_sub_word("not", "not", s)
    s = re_sub_word("and", "and", s)
    s = re_sub_word("or", "or", s)
    
    # Handle implies: A implies B -> (not (A) or (B))
    while "implies" in s:
        parts = s.split("implies", 1)
        s = f"(not ({parts[0]}) or ({parts[1]}))"
    
    # Handle iff: A iff B -> (A == B)
    while "iff" in s:
        parts = s.split("iff", 1)
        s = f"(({parts[0]}) == ({parts[1]}))"

    try:
        return bool(eval(s, {"__builtins__": None}, {}))
    except Exception as e:
        raise ValueError(f"Invalid propositional expression '{expr}': {e}")


def re_sub_word(word: str, replacement: str, text: str) -> str:
    import re
    return re.sub(rf'\b{re.escape(word)}\b', replacement, text)


def generate_truth_table(variables: List[str], formulas: List[str]) -> Dict[str, Any]:
    """Generates complete truth table for a set of variables and formulas."""
    variables = sorted(list(set(variables)))
    rows = []
    
    # Generate all 2^N assignments
    for combo in itertools.product([False, True], repeat=len(variables)):
        model = dict(zip(variables, combo))
        row_evals = {}
        for f in formulas:
            try:
                row_evals[f] = evaluate_prop_expr(f, model)
            except Exception:
                row_evals[f] = False
        rows.append({
            "assignment": model,
            "evaluations": row_evals
        })

    # Check tautology and satisfiability
    summary = {}
    for f in formulas:
        all_true = all(r["evaluations"][f] for r in rows)
        any_true = any(r["evaluations"][f] for r in rows)
        summary[f] = {
            "tautology": all_true,
            "satisfiable": any_true,
            "unsatisfiable": not any_true
        }

    return {
        "variables": variables,
        "formulas": formulas,
        "rows": rows,
        "summary": summary
    }


class Clause:
    def __init__(self, literals: Set[str], clause_id: Optional[str] = None):
        self.literals = frozenset(literals)
        self.id = clause_id or ""

    def __hash__(self):
        return hash(self.literals)

    def __eq__(self, other):
        return isinstance(other, Clause) and self.literals == other.literals

    def __str__(self):
        if not self.literals:
            return "□ (EMPTY_CONTRADICTION)"
        return " ∨ ".join(sorted(self.literals))

    def is_empty(self) -> bool:
        return len(self.literals) == 0


def resolve_clauses(c1: Clause, c2: Clause) -> List[Tuple[Clause, str]]:
    """Resolves two clauses on complementary literals (P and ~P)."""
    resolvents = []
    for lit in c1.literals:
        neg_lit = lit[1:] if lit.startswith("~") else f"~{lit}"
        if neg_lit in c2.literals:
            # Resolve on lit
            new_lits = (c1.literals - {lit}) | (c2.literals - {neg_lit})
            # Check for tautology like (P ∨ ~P)
            has_tautology = any((f"~{l}" in new_lits if not l.startswith("~") else l[1:] in new_lits) for l in new_lits)
            if not has_tautology:
                resolvents.append((Clause(new_lits), lit))
    return resolvents


def propositional_resolution(knowledge_base_clauses: List[List[str]], query_literal: Optional[str] = None) -> Dict[str, Any]:
    """Propositional resolution refutation theorem prover with step derivation."""
    clauses: Set[Clause] = set()
    steps: List[Dict[str, Any]] = []
    clause_counter = 0

    # Add KB clauses
    for lits in knowledge_base_clauses:
        clause_counter += 1
        c = Clause(set(lits), f"C{clause_counter}")
        clauses.add(c)
        steps.append({
            "step": clause_counter,
            "clause": str(c),
            "id": c.id,
            "origin": "Knowledge Base Premise"
        })

    # Add negated query for refutation proof
    if query_literal:
        neg_query = query_literal[1:] if query_literal.startswith("~") else f"~{query_literal}"
        clause_counter += 1
        neg_c = Clause({neg_query}, f"C{clause_counter}")
        clauses.add(neg_c)
        steps.append({
            "step": clause_counter,
            "clause": str(neg_c),
            "id": neg_c.id,
            "origin": f"Negated Query (~{query_literal})"
        })

    proved = False
    refutation_found = False

    while True:
        new_clauses: Set[Clause] = set()
        clause_list = list(clauses)

        for i in range(len(clause_list)):
            for j in range(i + 1, len(clause_list)):
                c1 = clause_list[i]
                c2 = clause_list[j]
                resolvent_pairs = resolve_clauses(c1, c2)

                for resolvent, resolved_on in resolvent_pairs:
                    if resolvent.is_empty():
                        clause_counter += 1
                        resolvent.id = f"C{clause_counter}"
                        steps.append({
                            "step": clause_counter,
                            "clause": str(resolvent),
                            "id": resolvent.id,
                            "parents": [c1.id, c2.id],
                            "resolved_on": resolved_on,
                            "origin": f"Resolved {c1.id} ({c1}) and {c2.id} ({c2}) on literal '{resolved_on}'",
                            "contradiction": True
                        })
                        refutation_found = True
                        proved = True
                        break

                    if resolvent not in clauses and resolvent not in new_clauses:
                        clause_counter += 1
                        resolvent.id = f"C{clause_counter}"
                        steps.append({
                            "step": clause_counter,
                            "clause": str(resolvent),
                            "id": resolvent.id,
                            "parents": [c1.id, c2.id],
                            "resolved_on": resolved_on,
                            "origin": f"Resolved {c1.id} and {c2.id} on '{resolved_on}'",
                            "contradiction": False
                        })
                        new_clauses.add(resolvent)

                if refutation_found:
                    break
            if refutation_found:
                break

        if refutation_found:
            break

        if new_clauses.issubset(clauses) or len(new_clauses) == 0:
            # No new clauses can be derived; refutation failed
            proved = False
            break

        clauses.update(new_clauses)
        if clause_counter > 80:  # Bound resolution search
            break

    return {
        "algorithm": "Propositional Resolution Refutation",
        "proved": proved,
        "entailed": proved if query_literal else None,
        "steps": steps,
        "total_clauses_generated": clause_counter,
        "explanation": f"Contradiction derived! Query '{query_literal}' is strictly entailed." if proved else f"Resolution terminated without empty clause. Query is not entailed by premises."
    }


# =====================================================================
# 2. FIRST-ORDER LOGIC UNIFICATION (MGU)
# =====================================================================

def is_variable(term: Any) -> bool:
    return isinstance(term, str) and term.startswith("?")


def parse_fol_term(s: str) -> Any:
    """Parses simple FOL term like P(a, ?x) into nested dict."""
    s = s.strip()
    if "(" not in s:
        return s
    pred, rest = s.split("(", 1)
    args_str = rest.rstrip(")")
    args = []
    # Simple comma split outside parens
    depth = 0
    curr = []
    for ch in args_str:
        if ch == "(" : depth += 1; curr.append(ch)
        elif ch == ")" : depth -= 1; curr.append(ch)
        elif ch == "," and depth == 0:
            args.append(parse_fol_term("".join(curr).strip()))
            curr = []
        else:
            curr.append(ch)
    if curr:
        args.append(parse_fol_term("".join(curr).strip()))
    return {"pred": pred.strip(), "args": args}


def apply_substitution(term: Any, theta: Dict[str, Any]) -> Any:
    if is_variable(term):
        return theta.get(term, term)
    if isinstance(term, dict) and "pred" in term:
        return {
            "pred": term["pred"],
            "args": [apply_substitution(a, theta) for a in term["args"]]
        }
    return term


def unify(x: Any, y: Any, theta: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Most General Unifier (MGU) algorithm with occurs-check."""
    if theta is None:
        theta = {}

    x = apply_substitution(x, theta)
    y = apply_substitution(y, theta)

    if x == y:
        return theta
    if is_variable(x):
        return unify_var(x, y, theta)
    if is_variable(y):
        return unify_var(y, x, theta)

    if isinstance(x, dict) and isinstance(y, dict):
        if x.get("pred") != y.get("pred") or len(x.get("args", [])) != len(y.get("args", [])):
            return None
        for a1, a2 in zip(x["args"], y["args"]):
            theta = unify(a1, a2, theta)
            if theta is None:
                return None
        return theta

    return None


def unify_var(var: str, x: Any, theta: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if var in theta:
        return unify(theta[var], x, theta)
    if is_variable(x) and x in theta:
        return unify(var, theta[x], theta)
    if occurs_check(var, x):
        return None  # Circular reference prevented
    new_theta = dict(theta)
    new_theta[var] = x
    return new_theta


def occurs_check(var: str, x: Any) -> bool:
    if var == x:
        return True
    if isinstance(x, dict) and "args" in x:
        return any(occurs_check(var, a) for a in x["args"])
    return False


def fol_unify_demonstration(expr1: str, expr2: str) -> Dict[str, Any]:
    """Interactive unification tester."""
    t1 = parse_fol_term(expr1)
    t2 = parse_fol_term(expr2)
    mgu = unify(t1, t2, {})
    return {
        "algorithm": "First-Order Logic Most General Unifier (MGU)",
        "expression1": expr1,
        "expression2": expr2,
        "unifiable": mgu is not None,
        "substitution": mgu if mgu is not None else None,
        "unified_result": str(apply_substitution(t1, mgu)) if mgu is not None else None,
        "explanation": f"Successfully unified with substitution: {mgu}" if mgu is not None else "Expressions cannot be unified due to symbol clash or occurs-check failure."
    }


# =====================================================================
# 3. CONSTRAINT SATISFACTION PROBLEM (CSP) ENGINE
# =====================================================================

class CSP:
    def __init__(self, variables: List[str], domains: Dict[str, List[Any]]):
        self.variables = variables
        self.domains = {v: list(domains[v]) for v in variables}
        self.constraints: List[Dict[str, Any]] = []

    def add_binary_constraint(self, var1: str, var2: str, condition_fn: Callable[[Any, Any], bool], description: str):
        self.constraints.append({
            "type": "binary",
            "vars": (var1, var2),
            "fn": condition_fn,
            "description": description
        })

    def is_consistent(self, var: str, value: Any, assignment: Dict[str, Any]) -> bool:
        test_assignment = dict(assignment)
        test_assignment[var] = value
        for c in self.constraints:
            v1, v2 = c["vars"]
            if v1 in test_assignment and v2 in test_assignment:
                if not c["fn"](test_assignment[v1], test_assignment[v2]):
                    return False
        return True


def solve_csp_backtracking(csp: CSP, use_mrv: bool = True) -> Dict[str, Any]:
    """CSP solver using backtracking search with MRV heuristic and step-by-step trace."""
    steps: List[Dict[str, Any]] = []
    step_counter = 0

    def select_unassigned_variable(assignment: Dict[str, Any], domains: Dict[str, List[Any]]) -> str:
        unassigned = [v for v in csp.variables if v not in assignment]
        if not use_mrv:
            return unassigned[0]
        # MRV heuristic: choose variable with fewest remaining legal values
        return min(unassigned, key=lambda v: len(domains[v]))

    def backtrack(assignment: Dict[str, Any], domains: Dict[str, List[Any]]) -> Optional[Dict[str, Any]]:
        nonlocal step_counter
        if len(assignment) == len(csp.variables):
            return assignment

        var = select_unassigned_variable(assignment, domains)
        for val in domains[var]:
            step_counter += 1
            consistent = csp.is_consistent(var, val, assignment)
            
            steps.append({
                "step": step_counter,
                "action": f"Assigning '{var}' = {val}",
                "variable": var,
                "value": val,
                "consistent": consistent,
                "current_assignment": dict(assignment)
            })

            if consistent:
                assignment[var] = val
                # Forward checking / domain reduction
                new_domains = {v: list(d) for v, d in domains.items()}
                new_domains[var] = [val]

                failure = False
                for other in csp.variables:
                    if other not in assignment:
                        legal_vals = [cand for cand in new_domains[other] if csp.is_consistent(other, cand, assignment)]
                        new_domains[other] = legal_vals
                        if not legal_vals:
                            failure = True
                            break

                if not failure:
                    result = backtrack(assignment, new_domains)
                    if result is not None:
                        return result

                # Backtrack
                step_counter += 1
                steps.append({
                    "step": step_counter,
                    "action": f"Backtracking from '{var}' = {val} (dead-end reached)",
                    "variable": var,
                    "current_assignment": dict(assignment)
                })
                del assignment[var]

        return None

    initial_assignment: Dict[str, Any] = {}
    solution = backtrack(initial_assignment, csp.domains)

    return {
        "algorithm": "CSP Backtracking with MRV & Forward Checking",
        "solved": solution is not None,
        "solution": solution,
        "steps": steps,
        "total_search_steps": step_counter,
        "variables": csp.variables,
        "explanation": f"Consistent assignment found satisfying all {len(csp.constraints)} constraints." if solution else "Problem is unsatisfiable: no assignment satisfies all constraints simultaneously."
    }
