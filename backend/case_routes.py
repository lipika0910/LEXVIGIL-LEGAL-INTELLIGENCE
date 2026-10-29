"""API Routes for Case Intelligence, Workspace, Ingestion, Reasoning, and AI Algorithm Lab."""
import json
import math
import re
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from pydantic import BaseModel, Field

from .cases import CaseManager
from .search_engine import CaseSearchIndex, tokenize
from .graph_algorithms import Graph, bfs, dfs, uniform_cost_search, greedy_best_first_search, astar_search, hill_climbing
from .reasoning_engine import ReasoningEngine
from .logic_csp import generate_truth_table, propositional_resolution, fol_unify_demonstration, CSP, solve_csp_backtracking
from .ai_lab import minimax, alpha_beta_search, mcts_demonstration, expectiminimax, train_supervised_classifier, kmeans_clustering, run_q_learning
from .demo_case import load_fictional_demo_case
from .judicial_records import GLOBAL_PRECEDENT_ENGINE


# In-memory search index cache per case
SEARCH_INDEXES: Dict[str, CaseSearchIndex] = {}


def get_search_index(case_id: str, cm: CaseManager) -> CaseSearchIndex:
    if case_id not in SEARCH_INDEXES:
        idx = CaseSearchIndex()
        docs = cm.list_documents(case_id)
        for d in docs:
            full_doc = cm.get_document(d["id"], case_id)
            if full_doc:
                idx.add_document(d["id"], d["filename"], full_doc.get("extracted_text", ""), full_doc.get("metadata", {}), full_doc.get("pages", []))
        SEARCH_INDEXES[case_id] = idx
    return SEARCH_INDEXES[case_id]


# Pydantic Schemas for Requests
class CaseCreateInput(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    reference: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=2, max_length=100)
    parties: List[str] = Field(default_factory=list)
    jurisdiction: str = Field(default="")
    court: str = Field(default="")
    description: str = Field(default="")
    tags: List[str] = Field(default_factory=list)


class CaseUpdateInput(BaseModel):
    title: Optional[str] = None
    reference: Optional[str] = None
    category: Optional[str] = None
    parties: Optional[List[str]] = None
    jurisdiction: Optional[str] = None
    court: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None


class FactCreateInput(BaseModel):
    document_id: str
    text: str = Field(min_length=1)
    entity: str = Field(default="")
    category: str = Field(default="Factual Assertion")
    fact_type: str = Field(default="user_input")
    page: Optional[int] = None
    status: str = Field(default="candidate")
    confidence: Optional[float] = None


class FactStatusUpdate(BaseModel):
    status: str = Field(description="'candidate', 'confirmed', or 'rejected'")


class EvidenceItemInput(BaseModel):
    title: str = Field(min_length=2)
    category: str = Field(default="Documentary")
    description: str = Field(default="")
    source_doc_id: Optional[str] = None
    page: Optional[int] = None
    status: str = Field(default="verified")


class RelationshipInput(BaseModel):
    source_id: str
    target_id: str
    relation_type: str = Field(default="relates_to")
    explanation: str = Field(default="")
    is_suggested: bool = False
    is_confirmed: bool = True


class PathfindingInput(BaseModel):
    algorithm: str = Field(default="bfs", description="'bfs', 'dfs', 'ucs', 'greedy', or 'astar'")
    source_id: str
    target_id: str


class SearchInput(BaseModel):
    query: str = Field(min_length=1)
    method: str = Field(default="bm25", description="'bm25', 'tfidf', 'exact', or 'phrase'")
    document_filter: Optional[str] = None


class TimelineEventInput(BaseModel):
    date_str: str = Field(min_length=4)
    title: str = Field(min_length=2)
    description: str = Field(default="")
    document_id: Optional[str] = None
    party: str = Field(default="")
    verification_status: str = Field(default="verified")


class InconsistencyInput(BaseModel):
    issue_type: str
    title: str
    explanation: str
    item_a_id: Optional[str] = None
    item_b_id: Optional[str] = None
    severity: str = "MEDIUM"
    status: str = "flagged"


class InconsistencyStatusUpdate(BaseModel):
    status: str = Field(description="'flagged', 'reviewed', or 'resolved'")


class RuleCreateInput(BaseModel):
    name: str = Field(min_length=2)
    description: str = Field(default="")
    premises: List[Dict[str, Any]]
    conclusion: Dict[str, Any]


class BackwardChainInput(BaseModel):
    goal_predicate: str
    goal_args: List[str]


class ArgumentInput(BaseModel):
    issue_title: str
    argument_text: str
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    assumptions: str = Field(default="")
    counterarguments: str = Field(default="")
    status: str = Field(default="proposed")


class AuthorityInput(BaseModel):
    title: str
    citation: str
    jurisdiction: str
    authority_type: str
    url: str = Field(default="")
    notes: str = Field(default="")
    verification_status: str = Field(default="verified")


class SavedAnalysisInput(BaseModel):
    analysis_type: str
    title: str
    data: Dict[str, Any]


class PrecedentAnalyzeInput(BaseModel):
    title: str = "Adjudicated Precedent"
    citation: str = ""
    court: str = "Commercial Court"
    text: str
    category: str = "Commercial Precedent"


class PrecedentSheetInput(BaseModel):
    precedent_ids: List[str] = Field(default_factory=list)


# AI Lab Request Models
class SearchLabInput(BaseModel):
    algorithm: str = Field(default="bfs")
    start_node: str = Field(default="A")
    target_node: str = Field(default="G")
    graph_data: Optional[Dict[str, Any]] = None


class LogicLabInput(BaseModel):
    mode: str = Field(default="truth_table", description="'truth_table', 'resolution', or 'unification'")
    variables: Optional[List[str]] = None
    formulas: Optional[List[str]] = None
    clauses: Optional[List[List[str]]] = None
    query: Optional[str] = None
    expr1: Optional[str] = None
    expr2: Optional[str] = None


class CSPLabInput(BaseModel):
    problem_type: str = Field(default="hearing_schedule", description="'hearing_schedule', 'event_timeline', or 'custom'")
    variables: Optional[List[str]] = None
    domains: Optional[Dict[str, List[Any]]] = None


class GameLabInput(BaseModel):
    algorithm: str = Field(default="minimax", description="'minimax', 'alpha_beta', 'mcts', or 'expectiminimax'")
    depth: int = Field(default=3)
    iterations: int = Field(default=30)


class RLLabInput(BaseModel):
    episodes: int = Field(default=120, ge=10, le=1000)
    alpha: float = Field(default=0.2, ge=0.01, le=1.0)
    gamma: float = Field(default=0.9, ge=0.1, le=0.99)
    epsilon: float = Field(default=0.3, ge=0.0, le=1.0)


def install_case_routes(app, db, owner_dependency):
    """Installs all Case Management, Intelligence, Workspace, and Lab routes."""
    cm = CaseManager(db)
    router = APIRouter(prefix="/api", tags=["case_intelligence"])

    # -------------------------------------------------------------
    # 1. CASE MANAGEMENT
    # -------------------------------------------------------------
    @router.get("/cases")
    def list_cases(status: Optional[str] = None, search: Optional[str] = None, uid: str = Depends(owner_dependency)):
        return cm.list_cases(uid, status=status, search=search)

    @router.post("/cases")
    def create_case(body: CaseCreateInput, uid: str = Depends(owner_dependency)):
        return cm.create_case(
            owner=uid,
            title=body.title,
            reference=body.reference,
            category=body.category,
            parties=body.parties,
            jurisdiction=body.jurisdiction,
            court=body.court,
            description=body.description,
            tags=body.tags
        )

    @router.post("/cases/demo")
    def create_demo_case(uid: str = Depends(owner_dependency)):
        demo = load_fictional_demo_case(cm, uid)
        # Refresh search index
        SEARCH_INDEXES.pop(demo["id"], None)
        get_search_index(demo["id"], cm)
        return demo

    @router.get("/cases/{cid}")
    def get_case_details(cid: str, uid: str = Depends(owner_dependency)):
        c = cm.get_case(cid, uid)
        if not c:
            raise HTTPException(404, "Case not found.")
        return c

    @router.put("/cases/{cid}")
    def update_case_details(cid: str, body: CaseUpdateInput, uid: str = Depends(owner_dependency)):
        c = cm.get_case(cid, uid)
        if not c:
            raise HTTPException(404, "Case not found.")
        updated = cm.update_case(cid, uid, **body.model_dump(exclude_unset=True))
        return updated

    @router.delete("/cases/{cid}")
    def delete_case(cid: str, uid: str = Depends(owner_dependency)):
        c = cm.get_case(cid, uid)
        if not c:
            raise HTTPException(404, "Case not found.")
        cm.delete_case(cid, uid)
        SEARCH_INDEXES.pop(cid, None)
        return {"deleted": True, "case_id": cid}

    # -------------------------------------------------------------
    # 2. DOCUMENT INGESTION & FACT EXTRACTION
    # -------------------------------------------------------------
    @router.get("/cases/{cid}/documents")
    def list_case_documents(cid: str, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        return cm.list_documents(cid)

    @router.post("/cases/{cid}/documents")
    async def upload_case_document(cid: str, file: UploadFile = File(...), ocr_language: str = Form(default=""), uid: str = Depends(owner_dependency)):
        case = cm.get_case(cid, uid)
        if not case:
            raise HTTPException(404, "Case not found.")

        data = await file.read(15 * 1024 * 1024 + 1)
        if len(data) > 15 * 1024 * 1024:
            raise HTTPException(413, "Document exceeds 15 MB limit.")

        filename = file.filename or "document.txt"
        file_ext = filename.split(".")[-1].lower() if "." in filename else "txt"

        # Deterministic text extraction
        pages = []
        try:
            if file_ext in ("pdf", "docx"):
                from .engine import extract
                pages = extract(data, filename, ocr_language)
                extracted_text = "\n\n".join(p.get("text", "") for p in pages)
            else:
                extracted_text = data.decode("utf-8", errors="replace")
                pages = [{"page": 1, "text": extracted_text}]
        except Exception as e:
            extracted_text = data.decode("utf-8", errors="replace")
            pages = [{"page": 1, "text": extracted_text}]

        doc = cm.add_document(
            case_id=cid,
            owner=uid,
            filename=filename,
            file_type=file_ext,
            file_size=len(data),
            text_content=extracted_text,
            pages=pages,
            metadata={"ocr_language": ocr_language, "page_count": len(pages)}
        )

        # Update in-memory search index
        idx = get_search_index(cid, cm)
        idx.add_document(doc["id"], filename, extracted_text, doc.get("metadata", {}), pages)

        # Automatic initial fact candidate detection
        _auto_extract_facts_from_text(cm, cid, doc["id"], extracted_text)

        return doc

    @router.get("/cases/{cid}/documents/{did}")
    def get_case_document(cid: str, did: str, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        doc = cm.get_document(did, cid)
        if not doc:
            raise HTTPException(404, "Document not found.")
        return doc

    @router.delete("/cases/{cid}/documents/{did}")
    def delete_case_document(cid: str, did: str, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        ok = cm.delete_document(did, cid)
        if not ok:
            raise HTTPException(404, "Document not found.")
        if cid in SEARCH_INDEXES:
            SEARCH_INDEXES[cid].remove_document(did)
        return {"deleted": True, "document_id": did}

    # -------------------------------------------------------------
    # 3. FACTS & FACT EXTRACTION
    # -------------------------------------------------------------
    @router.get("/cases/{cid}/facts")
    def list_facts(cid: str, category: Optional[str] = None, status: Optional[str] = None, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        return cm.list_facts(cid, category=category, status=status)

    @router.post("/cases/{cid}/facts")
    def create_fact(cid: str, body: FactCreateInput, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        return cm.add_fact(
            case_id=cid,
            document_id=body.document_id,
            text_span=body.text,
            entity=body.entity,
            category=body.category,
            fact_type=body.fact_type,
            page=body.page,
            status=body.status,
            confidence=body.confidence
        )

    @router.patch("/cases/{cid}/facts/{fid}/status")
    def update_fact_status(cid: str, fid: str, body: FactStatusUpdate, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        ok = cm.update_fact_status(fid, cid, body.status)
        if not ok:
            raise HTTPException(404, "Fact not found.")
        return {"updated": True, "fact_id": fid, "status": body.status}

    # -------------------------------------------------------------
    # 4. EVIDENCE & EVIDENCE GRAPH & PATHFINDING
    # -------------------------------------------------------------
    @router.get("/cases/{cid}/evidence")
    def list_evidence(cid: str, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        return cm.list_evidence_items(cid)

    @router.post("/cases/{cid}/evidence")
    def add_evidence(cid: str, body: EvidenceItemInput, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        return cm.add_evidence_item(
            case_id=cid,
            title=body.title,
            category=body.category,
            description=body.description,
            source_doc_id=body.source_doc_id,
            page=body.page,
            status=body.status
        )

    @router.get("/cases/{cid}/evidence/relationships")
    def list_relationships(cid: str, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        return cm.list_evidence_relationships(cid)

    @router.post("/cases/{cid}/evidence/relationships")
    def add_relationship(cid: str, body: RelationshipInput, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        return cm.add_evidence_relationship(
            case_id=cid,
            source_id=body.source_id,
            target_id=body.target_id,
            relation_type=body.relation_type,
            explanation=body.explanation,
            is_suggested=body.is_suggested,
            is_confirmed=body.is_confirmed
        )

    @router.get("/cases/{cid}/evidence/graph")
    def get_evidence_graph(cid: str, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        items = cm.list_evidence_items(cid)
        rels = cm.list_evidence_relationships(cid)
        
        # Build node positions in a clean circular / layered layout
        nodes = []
        n_count = len(items)
        for i, item in enumerate(items):
            angle = (2 * math.pi * i) / (n_count or 1)
            radius = 220
            nodes.append({
                "id": item["id"],
                "label": item["title"],
                "category": item["category"],
                "status": item["status"],
                "doc_name": item.get("filename", ""),
                "description": item["description"],
                "x": round(350 + radius * math.cos(angle), 1),
                "y": round(260 + radius * math.sin(angle), 1)
            })

        edges = []
        for r in rels:
            edges.append({
                "id": r["id"],
                "source": r["source_id"],
                "target": r["target_id"],
                "relation": r["relation_type"],
                "explanation": r["explanation"],
                "is_confirmed": bool(r.get("is_confirmed", 1))
            })

        return {"nodes": nodes, "edges": edges}

    @router.post("/cases/{cid}/evidence/pathfinding")
    def find_evidence_path(cid: str, body: PathfindingInput, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        items = cm.list_evidence_items(cid)
        rels = cm.list_evidence_relationships(cid)

        # Construct Graph
        g = Graph(directed=False)
        item_dict = {it["id"]: it for it in items}
        for it in items:
            g.add_node(it["id"], label=it["title"])
        for r in rels:
            g.add_edge(r["source_id"], r["target_id"], weight=1.0, relation=r["relation_type"])

        algo = body.algorithm.lower()
        if algo == "dfs":
            res = dfs(g, body.source_id, body.target_id)
        elif algo == "ucs":
            res = uniform_cost_search(g, body.source_id, body.target_id)
        elif algo == "greedy":
            res = greedy_best_first_search(g, body.source_id, body.target_id)
        elif algo == "astar":
            res = astar_search(g, body.source_id, body.target_id)
        else:
            res = bfs(g, body.source_id, body.target_id)

        # Enrich path with item labels
        res["path_nodes"] = [item_dict.get(nid, {"id": nid, "title": nid}) for nid in res.get("path", [])]
        return res

    # -------------------------------------------------------------
    # 5. INTELLIGENT SEARCH
    # -------------------------------------------------------------
    @router.post("/cases/{cid}/search")
    def search_case(cid: str, body: SearchInput, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        idx = get_search_index(cid, cm)
        m = body.method.lower()
        if m == "exact":
            return idx.search_exact(body.query, body.document_filter)
        elif m == "phrase":
            return idx.search_phrase(body.query, body.document_filter)
        elif m == "tfidf":
            return idx.search_tfidf(body.query, body.document_filter)
        else:
            return idx.search_bm25(body.query, body.document_filter)

    # -------------------------------------------------------------
    # 6. TIMELINE & INCONSISTENCIES
    # -------------------------------------------------------------
    @router.get("/cases/{cid}/timeline")
    def list_timeline(cid: str, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        return cm.list_timeline_events(cid)

    @router.post("/cases/{cid}/timeline")
    def add_timeline_event(cid: str, body: TimelineEventInput, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        return cm.add_timeline_event(
            case_id=cid,
            date_str=body.date_str,
            title=body.title,
            description=body.description,
            document_id=body.document_id,
            party=body.party,
            verification_status=body.verification_status
        )

    @router.get("/cases/{cid}/inconsistencies")
    def list_inconsistencies(cid: str, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        return cm.list_inconsistencies(cid)

    @router.post("/cases/{cid}/inconsistencies")
    def add_inconsistency(cid: str, body: InconsistencyInput, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        return cm.add_inconsistency(
            case_id=cid,
            issue_type=body.issue_type,
            title=body.title,
            explanation=body.explanation,
            item_a_id=body.item_a_id,
            item_b_id=body.item_b_id,
            severity=body.severity,
            status=body.status
        )

    @router.patch("/cases/{cid}/inconsistencies/{iid}/status")
    def update_inconsistency_status(cid: str, iid: str, body: InconsistencyStatusUpdate, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        ok = cm.update_inconsistency_status(iid, cid, body.status)
        if not ok:
            raise HTTPException(404, "Inconsistency record not found.")
        return {"updated": True, "id": iid, "status": body.status}

    # -------------------------------------------------------------
    # 7. KNOWLEDGE-BASED REASONING
    # -------------------------------------------------------------
    @router.get("/cases/{cid}/reasoning/rules")
    def list_rules(cid: str, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        with cm.db.connect() as con:
            from sqlalchemy import text
            rows = con.execute(text("SELECT * FROM reasoning_rules WHERE case_id = :cid ORDER BY created_at ASC"), {"cid": cid}).mappings().all()
            res = []
            for r in rows:
                item = dict(r)
                item["rule"] = json.loads(item.get("rule_json") or "{}")
                res.append(item)
            return res

    @router.post("/cases/{cid}/reasoning/rules")
    def add_rule(cid: str, body: RuleCreateInput, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        import secrets, time
        rid = "RULE-" + secrets.token_hex(6)
        now = time.time()
        rule_data = {"premises": body.premises, "conclusion": body.conclusion}
        with cm.db.begin() as con:
            from sqlalchemy import text
            con.execute(text("""
                INSERT INTO reasoning_rules (id, case_id, name, description, rule_json, created_at)
                VALUES (:id, :case_id, :name, :description, :rule_json, :now)
            """), {
                "id": rid,
                "case_id": cid,
                "name": body.name,
                "description": body.description,
                "rule_json": json.dumps(rule_data),
                "now": now
            })
        return {"id": rid, "name": body.name, "description": body.description, "rule": rule_data}

    @router.post("/cases/{cid}/reasoning/forward")
    def run_forward_chaining(cid: str, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        engine = _build_reasoning_engine(cm, cid)
        res = engine.forward_chain()
        # Check contradictions too
        res["contradictions_detected"] = engine.check_contradictions()
        return res

    @router.post("/cases/{cid}/reasoning/backward")
    def run_backward_chaining(cid: str, body: BackwardChainInput, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        engine = _build_reasoning_engine(cm, cid)
        return engine.backward_chain(body.goal_predicate, body.goal_args)

    # -------------------------------------------------------------
    # 8. ARGUMENTS & AUTHORITIES
    # -------------------------------------------------------------
    @router.get("/cases/{cid}/arguments")
    def list_arguments(cid: str, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        return cm.list_arguments(cid)

    @router.post("/cases/{cid}/arguments")
    def add_argument(cid: str, body: ArgumentInput, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        return cm.add_argument(
            case_id=cid,
            issue_title=body.issue_title,
            argument_text=body.argument_text,
            supporting_evidence_ids=body.supporting_evidence_ids,
            assumptions=body.assumptions,
            counterarguments=body.counterarguments,
            status=body.status
        )

    @router.get("/cases/{cid}/authorities")
    def list_authorities(cid: str, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        return cm.list_authorities(cid)

    @router.post("/cases/{cid}/authorities")
    def add_authority(cid: str, body: AuthorityInput, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        return cm.add_authority(
            case_id=cid,
            title=body.title,
            citation=body.citation,
            jurisdiction=body.jurisdiction,
            authority_type=body.authority_type,
            url=body.url,
            notes=body.notes,
            verification_status=body.verification_status
        )

    # -------------------------------------------------------------
    # 9. SAVED ANALYSES & CASE REPORT PREVIEW
    # -------------------------------------------------------------
    @router.get("/cases/{cid}/saved")
    def list_saved_analyses(cid: str, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        return cm.list_saved_analyses(cid, uid)

    @router.post("/cases/{cid}/saved")
    def save_analysis(cid: str, body: SavedAnalysisInput, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        return cm.save_case_analysis(cid, uid, body.analysis_type, body.title, body.data)

    @router.get("/cases/{cid}/report")
    def generate_case_report(cid: str, uid: str = Depends(owner_dependency)):
        c = cm.get_case(cid, uid)
        if not c:
            raise HTTPException(404, "Case not found.")

        docs = cm.list_documents(cid)
        facts = cm.list_facts(cid)
        evidence = cm.list_evidence_items(cid)
        rels = cm.list_evidence_relationships(cid)
        timeline = cm.list_timeline_events(cid)
        inconsistencies = cm.list_inconsistencies(cid)
        args = cm.list_arguments(cid)
        auths = cm.list_authorities(cid)

        # Markdown formatted report
        md_lines = [
            f"# LEXVIGIL AI — CASE PREPARATION REPORT",
            f"**Case Title:** {c['title']}",
            f"**Reference:** {c['reference']} | **Category:** {c['category']}",
            f"**Jurisdiction:** {c.get('jurisdiction', 'Not specified')} | **Court:** {c.get('court', 'Not specified')}",
            f"**Parties:** {', '.join(c.get('parties', []))}",
            f"\n## 1. Executive Summary",
            c.get("description", "No description provided."),
            f"\n## 2. Document Inventory ({len(docs)} documents)",
        ]
        for d in docs:
            md_lines.append(f"- **{d['filename']}** ({d['file_type'].upper()}, {d['file_size']} bytes)")

        md_lines.append(f"\n## 3. Extracted Facts & Findings ({len(facts)} items)")
        for f in facts:
            status_tag = f"[{f['status'].upper()}]"
            md_lines.append(f"- {status_tag} **{f['category']}:** {f['text']} *(Entity: {f.get('entity', 'N/A')}, Source: {f.get('filename', 'doc')})*")

        md_lines.append(f"\n## 4. Chronological Timeline ({len(timeline)} events)")
        for t in timeline:
            md_lines.append(f"- **{t['date_str']}:** {t['title']} — {t['description']} *(Party: {t.get('party', '')})*")

        md_lines.append(f"\n## 5. Potential Inconsistencies & Discrepancies ({len(inconsistencies)} flagged)")
        for inc in inconsistencies:
            md_lines.append(f"- **[{inc['severity']}] {inc['title']}:** {inc['explanation']} *(Status: {inc['status']})*")

        md_lines.append(f"\n## 6. Strategic Arguments & Counterarguments ({len(args)} issues)")
        for a in args:
            md_lines.append(f"### Issue: {a['issue_title']}")
            md_lines.append(f"**Affirmative Argument:** {a['argument_text']}")
            if a.get('counterarguments'):
                md_lines.append(f"**Counterargument / Risk:** {a['counterarguments']}")
            if a.get('assumptions'):
                md_lines.append(f"**Assumptions:** {a['assumptions']}")

        md_lines.append(f"\n## 7. Relevant Legal Authorities ({len(auths)} cited)")
        for au in auths:
            md_lines.append(f"- **{au['title']}** ({au['citation']}) — {au['notes']}")

        md_lines.append("\n---\n*Report generated by LexVigil AI Legal Intelligence. Professional human review required before filing.*")

        return {
            "case": c,
            "counts": {
                "documents": len(docs),
                "facts": len(facts),
                "evidence": len(evidence),
                "relationships": len(rels),
                "timeline_events": len(timeline),
                "inconsistencies": len(inconsistencies),
                "arguments": len(args),
                "authorities": len(auths)
            },
            "markdown": "\n".join(md_lines)
        }

    # -------------------------------------------------------------
    # 10. INTERACTIVE AI ALGORITHM LAB
    # -------------------------------------------------------------
    @router.post("/lab/search")
    def run_lab_search(body: SearchLabInput):
        # Default sample legal graph
        g = Graph(directed=False)
        nodes = [
            ("A", "Client_Intake", 100, 100),
            ("B", "Retainer_Agreement", 220, 70),
            ("C", "Document_Discovery", 220, 150),
            ("D", "Statutory_Notice", 360, 50),
            ("E", "Settlement_Conference", 360, 150),
            ("F", "Arbitration_Filing", 480, 80),
            ("G", "Final_Award", 600, 100)
        ]
        for nid, lbl, x, y in nodes:
            g.add_node(nid, label=lbl, x=x, y=y)

        edges = [
            ("A", "B", 1.0), ("A", "C", 2.0),
            ("B", "D", 2.5), ("B", "C", 1.5),
            ("C", "E", 1.0), ("D", "F", 3.0),
            ("E", "F", 2.0), ("E", "G", 4.5),
            ("F", "G", 1.5)
        ]
        for u, v, w in edges:
            g.add_edge(u, v, weight=w)

        algo = body.algorithm.lower()
        if algo == "dfs":
            res = dfs(g, body.start_node, body.target_node)
        elif algo == "ucs":
            res = uniform_cost_search(g, body.start_node, body.target_node)
        elif algo == "greedy":
            res = greedy_best_first_search(g, body.start_node, body.target_node)
        elif algo == "astar":
            res = astar_search(g, body.start_node, body.target_node)
        elif algo == "hill_climbing":
            # State values for local search demo
            state_vals = {"A": 1.0, "B": 2.5, "C": 2.0, "D": 4.0, "E": 3.8, "F": 5.5, "G": 7.0}
            neighbors = {"A": ["B", "C"], "B": ["A", "D", "C"], "C": ["A", "B", "E"], "D": ["B", "F"], "E": ["C", "F", "G"], "F": ["D", "E", "G"], "G": ["E", "F"]}
            res = hill_climbing(state_vals, neighbors, body.start_node)
        else:
            res = bfs(g, body.start_node, body.target_node)

        res["graph_nodes"] = [{"id": n["id"], "label": n["label"], "x": n["x"], "y": n["y"]} for n in g.nodes.values()]
        res["graph_edges"] = [{"u": u, "v": e["target"], "w": e["weight"]} for u in g.adj for e in g.adj[u] if u < e["target"]]
        return res

    @router.post("/lab/game")
    def run_lab_game(body: GameLabInput):
        algo = body.algorithm.lower()
        if algo == "mcts":
            return mcts_demonstration(iterations=body.iterations)
        elif algo == "expectiminimax":
            # Litigation expectation tree
            tree = {
                "name": "Litigation_Decision", "type": "max",
                "children": [
                    {
                        "name": "Accept_Settlement_Offer", "type": "leaf", "value": 50.0
                    },
                    {
                        "name": "Proceed_To_Trial", "type": "chance",
                        "children": [
                            {"name": "Favorable_Judgment", "type": "leaf", "value": 100.0, "prob": 0.65},
                            {"name": "Adverse_Judgment", "type": "leaf", "value": -20.0, "prob": 0.35}
                        ]
                    }
                ]
            }
            return expectiminimax(tree)
        elif algo == "alpha_beta":
            # 3-level game tree
            tree = {
                "name": "Root", "type": "max",
                "children": [
                    {
                        "name": "Branch_A", "type": "min",
                        "children": [
                            {"name": "A1", "value": 3.0},
                            {"name": "A2", "value": 5.0},
                            {"name": "A3", "value": 9.0}
                        ]
                    },
                    {
                        "name": "Branch_B", "type": "min",
                        "children": [
                            {"name": "B1", "value": 2.0},
                            {"name": "B2", "value": 1.0},
                            {"name": "B3", "value": 8.0}
                        ]
                    },
                    {
                        "name": "Branch_C", "type": "min",
                        "children": [
                            {"name": "C1", "value": 4.0},
                            {"name": "C2", "value": 6.0},
                            {"name": "C3", "value": 2.0}
                        ]
                    }
                ]
            }
            return alpha_beta_search(tree, depth=body.depth, alpha=-float("inf"), beta=float("inf"), is_maximizing=True)
        else:
            # Classic Minimax
            tree = {
                "name": "Root", "type": "max",
                "children": [
                    {
                        "name": "Action_Negotiate", "type": "min",
                        "children": [
                            {"name": "High_Counter", "value": 7.0},
                            {"name": "Low_Counter", "value": 4.0}
                        ]
                    },
                    {
                        "name": "Action_Litigate", "type": "min",
                        "children": [
                            {"name": "Full_Decree", "value": 9.0},
                            {"name": "Dismissal", "value": 1.0}
                        ]
                    }
                ]
            }
            return minimax(tree, depth=body.depth, is_maximizing=True)

    @router.post("/lab/logic")
    def run_lab_logic(body: LogicLabInput):
        mode = body.mode.lower()
        if mode == "resolution":
            # Default or custom propositional resolution
            clauses = body.clauses or [
                ["~Breach", "Damages"],           # Breach implies Damages
                ["Breach"],                      # Breach occurred
                ["~Damages", "Interest_Awarded"]  # Damages implies Interest
            ]
            query = body.query or "Interest_Awarded"
            return propositional_resolution(clauses, query)
        elif mode == "unification":
            e1 = body.expr1 or "Obligation(?contract, ?party, INR_1250000)"
            e2 = body.expr2 or "Obligation(EPC_Contract_3B, Metro_Rail, ?amount)"
            return fol_unify_demonstration(e1, e2)
        else:
            # Truth Table
            vars_list = body.variables or ["Contract_Valid", "Notice_Served", "Breach_Cured"]
            formulas = body.formulas or [
                "Contract_Valid and Notice_Served",
                "(Contract_Valid and Notice_Served) implies (not Breach_Cured)",
                "Contract_Valid iff Notice_Served"
            ]
            return generate_truth_table(vars_list, formulas)

    @router.post("/lab/csp")
    def run_lab_csp(body: CSPLabInput):
        ptype = body.problem_type.lower()
        if ptype == "event_timeline":
            # Temporal sequencing constraints for trial events
            variables = ["Notice_Delivery", "Cure_Period_Expiry", "Arbitral_Filing", "Award_Published"]
            domains = {v: [1, 2, 3, 4, 5, 6] for v in variables}
            csp = CSP(variables, domains)
            # Notice precedes Cure Expiry by at least 2 weeks
            csp.add_binary_constraint("Notice_Delivery", "Cure_Period_Expiry", lambda n, c: c >= n + 2, "Cure period expires at least 2 weeks after notice delivery")
            # Filing follows cure expiry
            csp.add_binary_constraint("Cure_Period_Expiry", "Arbitral_Filing", lambda c, f: f > c, "Arbitral filing must occur after cure expiry")
            # Award published after filing
            csp.add_binary_constraint("Arbitral_Filing", "Award_Published", lambda f, a: a >= f + 2, "Award published after arbitral filing")
            return solve_csp_backtracking(csp)
        else:
            # Courtroom Hearing & Judge Scheduling CSP
            # 3 Courtrooms: C1, C2, C3. 4 Cases: Arbitration, Commercial_Suit, Writ_Petition, Tax_Appeal
            variables = ["Case_Commercial", "Case_Arbitration", "Case_Writ", "Case_Tax"]
            # Available slots (Room_Time): e.g. Courtroom 1 Morning (1), Courtroom 1 Afternoon (2), Courtroom 2 Morning (3), Courtroom 2 Afternoon (4)
            domains = {
                "Case_Commercial": [1, 2, 3],
                "Case_Arbitration": [1, 2, 4],
                "Case_Writ": [2, 3, 4],
                "Case_Tax": [1, 3, 4]
            }
            csp = CSP(variables, domains)
            # All cases must be in distinct time/courtroom slots
            for v1, v2 in [("Case_Commercial", "Case_Arbitration"), ("Case_Commercial", "Case_Writ"), ("Case_Commercial", "Case_Tax"),
                           ("Case_Arbitration", "Case_Writ"), ("Case_Arbitration", "Case_Tax"), ("Case_Writ", "Case_Tax")]:
                csp.add_binary_constraint(v1, v2, lambda x, y: x != y, f"{v1} and {v2} cannot share the same court time slot")
            return solve_csp_backtracking(csp)

    @router.post("/lab/ml")
    def run_lab_ml(mode: str = "classification", k: int = 3):
        if mode == "clustering":
            return kmeans_clustering(k=k)
        return train_supervised_classifier()

    @router.post("/lab/rl")
    def run_lab_rl(body: RLLabInput):
        return run_q_learning(episodes=body.episodes, alpha=body.alpha, gamma=body.gamma, epsilon=body.epsilon)

    # -------------------------------------------------------------
    # 10. JUDICIAL RECORDS & PRECEDENT INTELLIGENCE
    # -------------------------------------------------------------
    @router.get("/precedents")
    def search_precedents(
        q: str = "",
        category: str = "All",
        court: str = "All",
        mode: str = "bm25"
    ):
        return GLOBAL_PRECEDENT_ENGINE.search_precedents(
            query=q,
            category_filter=category,
            court_filter=court,
            mode=mode
        )

    @router.get("/precedents/{pid}")
    def get_precedent_detail(pid: str):
        p = GLOBAL_PRECEDENT_ENGINE.get_precedent(pid)
        if not p:
            raise HTTPException(404, "Precedent not found.")
        return p

    @router.post("/precedents/extract")
    def analyze_custom_judgment(body: PrecedentAnalyzeInput):
        if not body.text.strip():
            raise HTTPException(422, "Judgment text content is required.")
        return GLOBAL_PRECEDENT_ENGINE.add_custom_judgment(body.title, body.citation, body.court, body.text, body.category)

    @router.post("/precedents/submission-sheet")
    def generate_submission_sheet(body: PrecedentSheetInput):
        markdown = GLOBAL_PRECEDENT_ENGINE.generate_court_submission_sheet(body.precedent_ids)
        return {"markdown": markdown}

    @router.post("/cases/{cid}/precedents/{pid}/attach")
    def attach_precedent_to_case(cid: str, pid: str, uid: str = Depends(owner_dependency)):
        cm.get_case(cid, uid)
        p = GLOBAL_PRECEDENT_ENGINE.get_precedent(pid)
        if not p:
            raise HTTPException(404, "Precedent not found.")
        auth = cm.add_authority(
            case_id=cid,
            title=p["title"],
            citation=p["citation"],
            jurisdiction=p["court"],
            authority_type="Judicial Precedent",
            url=f"/app/precedents?id={p['id']}",
            notes=f"Ratio: {p['ratio_decidendi']}"
        )
        return {"status": "attached", "authority": auth}

    app.include_router(router)


def _auto_extract_facts_from_text(cm: CaseManager, cid: str, did: str, text: str):
    """Helper regex/NLP pattern extractor for candidate facts."""
    # 1. Currency amounts (INR, Rs, ₹)
    currencies = re.finditer(r'(?:INR|Rs\.?|₹)\s*([\d,]+(?:\.\d{2})?)', text, re.I)
    for m in currencies:
        amt = m.group(0)
        span = m.span()
        cm.add_fact(cid, did, f"Financial amount recorded: {amt}", "Financial Record", "Payment", "currency_amount", page=1, span_start=span[0], span_end=span[1], status="candidate", confidence=0.92)

    # 2. Dates (YYYY-MM-DD or DD Month YYYY)
    dates = re.finditer(r'\b(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}|\d{4}-\d{2}-\d{2})\b', text, re.I)
    for m in dates:
        dt = m.group(0)
        span = m.span()
        cm.add_fact(cid, did, f"Date reference: {dt}", "Timeline Reference", "Temporal", "date_reference", page=1, span_start=span[0], span_end=span[1], status="candidate", confidence=0.95)

    # 3. Obligations and statutory notices
    if re.search(r'\bshall pay\b', text, re.I):
        cm.add_fact(cid, did, "Express payment obligation identified ('shall pay')", "Payment Term", "Obligation", "contract_covenant", page=1, status="candidate", confidence=0.88)
    if re.search(r'\bsection\s+73\b', text, re.I):
        cm.add_fact(cid, did, "Section 73 Indian Contract Act invoked for unliquidated breach damages", "Statutory Claim", "Claim", "statutory_provision", page=1, status="candidate", confidence=0.96)


def _build_reasoning_engine(cm: CaseManager, cid: str) -> ReasoningEngine:
    """Instantiates and populates the reasoning engine from case facts and rules."""
    engine = ReasoningEngine()
    facts = cm.list_facts(cid)
    for f in facts:
        # Map facts to predicates
        cat = f.get("category", "").lower()
        txt = f.get("text", "")
        ev = [f["id"]]
        if "paid" in txt.lower():
            engine.add_fact("payment_made", ["inv-2024-884", "inr_10_00_000"], ev)
        elif "billed" in txt.lower() or "invoice" in txt.lower():
            engine.add_fact("invoice_billed", ["inv-2024-884", "inr_12_50_000"], ev)
        elif "clearance" in txt.lower() or "approved" in txt.lower():
            engine.add_fact("inspection_clearance", ["milestone_3", "zero_defects"], ev)
        elif "crack" in txt.lower() or "defect" in txt.lower():
            engine.add_fact("allegation", ["milestone_3", "micro_cracks"], ev)
        elif "notice" in txt.lower():
            engine.add_fact("notice_served", ["apex", "metro_rail"], ev)

    # Load custom rules from DB
    with cm.db.connect() as con:
        from sqlalchemy import text
        rows = con.execute(text("SELECT * FROM reasoning_rules WHERE case_id = :cid"), {"cid": cid}).mappings().all()
        for r in rows:
            rule_dict = json.loads(r.get("rule_json") or "{}")
            if "premises" in rule_dict and "conclusion" in rule_dict:
                engine.add_rule(r["id"], r["name"], rule_dict["premises"], rule_dict["conclusion"], r.get("description", ""))

    return engine
