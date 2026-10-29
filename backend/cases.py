"""Case management, document storage, and relational models for LexVigil AI."""
import json
import secrets
import time
from typing import Any, Dict, List, Optional
from sqlalchemy import text
from sqlalchemy.engine import Engine


def init_case_tables(db: Engine):
    """Safely initialize schema tables for full legal intelligence platform."""
    with db.begin() as con:
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS cases (
                id TEXT PRIMARY KEY,
                owner TEXT NOT NULL,
                title TEXT NOT NULL,
                reference TEXT NOT NULL,
                category TEXT NOT NULL,
                parties_json TEXT NOT NULL DEFAULT '[]',
                jurisdiction TEXT NOT NULL DEFAULT '',
                court TEXT NOT NULL DEFAULT '',
                description TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'active',
                tags_json TEXT NOT NULL DEFAULT '[]',
                created_at DOUBLE PRECISION NOT NULL,
                updated_at DOUBLE PRECISION NOT NULL
            )
        """))
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS case_documents (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                owner TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                extracted_text TEXT NOT NULL,
                pages_json TEXT NOT NULL DEFAULT '[]',
                metadata_json TEXT NOT NULL DEFAULT '{}',
                created_at DOUBLE PRECISION NOT NULL
            )
        """))
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS case_facts (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                document_id TEXT NOT NULL,
                text TEXT NOT NULL,
                entity TEXT NOT NULL,
                category TEXT NOT NULL,
                fact_type TEXT NOT NULL,
                page INTEGER,
                span_start INTEGER,
                span_end INTEGER,
                status TEXT NOT NULL DEFAULT 'candidate',
                confidence DOUBLE PRECISION,
                created_at DOUBLE PRECISION NOT NULL
            )
        """))
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS evidence_items (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                source_doc_id TEXT,
                page INTEGER,
                status TEXT NOT NULL DEFAULT 'verified',
                created_at DOUBLE PRECISION NOT NULL
            )
        """))
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS evidence_relationships (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                explanation TEXT NOT NULL,
                is_suggested INTEGER NOT NULL DEFAULT 0,
                is_confirmed INTEGER NOT NULL DEFAULT 1,
                created_at DOUBLE PRECISION NOT NULL
            )
        """))
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS timeline_events (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                date_str TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                document_id TEXT,
                party TEXT NOT NULL DEFAULT '',
                verification_status TEXT NOT NULL DEFAULT 'unverified',
                created_at DOUBLE PRECISION NOT NULL
            )
        """))
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS inconsistencies (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                issue_type TEXT NOT NULL,
                title TEXT NOT NULL,
                explanation TEXT NOT NULL,
                item_a_id TEXT,
                item_b_id TEXT,
                status TEXT NOT NULL DEFAULT 'flagged',
                severity TEXT NOT NULL DEFAULT 'MEDIUM',
                created_at DOUBLE PRECISION NOT NULL
            )
        """))
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS reasoning_rules (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                rule_json TEXT NOT NULL,
                created_at DOUBLE PRECISION NOT NULL
            )
        """))
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS inference_runs (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                engine_type TEXT NOT NULL,
                query TEXT NOT NULL,
                trace_json TEXT NOT NULL DEFAULT '[]',
                conclusions_json TEXT NOT NULL DEFAULT '[]',
                created_at DOUBLE PRECISION NOT NULL
            )
        """))
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS arguments (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                issue_title TEXT NOT NULL,
                argument_text TEXT NOT NULL,
                supporting_evidence_ids TEXT NOT NULL DEFAULT '[]',
                assumptions TEXT NOT NULL DEFAULT '',
                counterarguments TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'proposed',
                created_at DOUBLE PRECISION NOT NULL
            )
        """))
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS legal_authorities (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                title TEXT NOT NULL,
                citation TEXT NOT NULL,
                jurisdiction TEXT NOT NULL,
                authority_type TEXT NOT NULL,
                url TEXT NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                verification_status TEXT NOT NULL DEFAULT 'unverified',
                created_at DOUBLE PRECISION NOT NULL
            )
        """))
        con.execute(text("""
            CREATE TABLE IF NOT EXISTS saved_analyses (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                owner TEXT NOT NULL,
                analysis_type TEXT NOT NULL,
                title TEXT NOT NULL,
                data_json TEXT NOT NULL,
                created_at DOUBLE PRECISION NOT NULL
            )
        """))


class CaseManager:
    """Manages cases, documents, facts, and relationships with owner and case isolation."""
    def __init__(self, db: Engine):
        self.db = db
        init_case_tables(db)

    def list_cases(self, owner: str, status: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.db.connect() as con:
            query = "SELECT * FROM cases WHERE owner = :owner"
            params: Dict[str, Any] = {"owner": owner}
            if status:
                query += " AND status = :status"
                params["status"] = status
            if search:
                query += " AND (title LIKE :search OR reference LIKE :search OR description LIKE :search)"
                params["search"] = f"%{search}%"
            query += " ORDER BY updated_at DESC"
            rows = con.execute(text(query), params).mappings().all()
            
            # Enrich with document and evidence counts
            cases = []
            for r in rows:
                c = dict(r)
                c["parties"] = json.loads(c.get("parties_json") or "[]")
                c["tags"] = json.loads(c.get("tags_json") or "[]")
                doc_count = con.execute(text("SELECT count(*) FROM case_documents WHERE case_id = :cid"), {"cid": c["id"]}).scalar() or 0
                fact_count = con.execute(text("SELECT count(*) FROM case_facts WHERE case_id = :cid"), {"cid": c["id"]}).scalar() or 0
                evidence_count = con.execute(text("SELECT count(*) FROM evidence_items WHERE case_id = :cid"), {"cid": c["id"]}).scalar() or 0
                inconsistency_count = con.execute(text("SELECT count(*) FROM inconsistencies WHERE case_id = :cid AND status != 'resolved'"), {"cid": c["id"]}).scalar() or 0
                c["doc_count"] = doc_count
                c["fact_count"] = fact_count
                c["evidence_count"] = evidence_count
                c["inconsistency_count"] = inconsistency_count
                cases.append(c)
            return cases

    def get_case(self, case_id: str, owner: str) -> Optional[Dict[str, Any]]:
        with self.db.connect() as con:
            row = con.execute(text("SELECT * FROM cases WHERE id = :id AND owner = :owner"), {"id": case_id, "owner": owner}).mappings().first()
            if not row:
                return None
            c = dict(row)
            c["parties"] = json.loads(c.get("parties_json") or "[]")
            c["tags"] = json.loads(c.get("tags_json") or "[]")
            c["doc_count"] = con.execute(text("SELECT count(*) FROM case_documents WHERE case_id = :cid"), {"cid": case_id}).scalar() or 0
            c["fact_count"] = con.execute(text("SELECT count(*) FROM case_facts WHERE case_id = :cid"), {"cid": case_id}).scalar() or 0
            c["evidence_count"] = con.execute(text("SELECT count(*) FROM evidence_items WHERE case_id = :cid"), {"cid": case_id}).scalar() or 0
            c["inconsistency_count"] = con.execute(text("SELECT count(*) FROM inconsistencies WHERE case_id = :cid"), {"cid": case_id}).scalar() or 0
            return c

    def create_case(self, owner: str, title: str, reference: str, category: str, parties: List[str], jurisdiction: str = "", court: str = "", description: str = "", tags: Optional[List[str]] = None) -> Dict[str, Any]:
        case_id = "CASE-" + secrets.token_hex(8)
        now = time.time()
        with self.db.begin() as con:
            con.execute(text("""
                INSERT INTO cases (id, owner, title, reference, category, parties_json, jurisdiction, court, description, status, tags_json, created_at, updated_at)
                VALUES (:id, :owner, :title, :reference, :category, :parties, :jurisdiction, :court, :description, 'active', :tags, :now, :now)
            """), {
                "id": case_id,
                "owner": owner,
                "title": title,
                "reference": reference,
                "category": category,
                "parties": json.dumps(parties),
                "jurisdiction": jurisdiction,
                "court": court,
                "description": description,
                "tags": json.dumps(tags or []),
                "now": now
            })
        return self.get_case(case_id, owner)

    def update_case(self, case_id: str, owner: str, **kwargs) -> Optional[Dict[str, Any]]:
        allowed = {"title", "reference", "category", "parties", "jurisdiction", "court", "description", "status", "tags"}
        updates = {}
        for k, v in kwargs.items():
            if k in allowed:
                if k in ("parties", "tags"):
                    updates[f"{k}_json"] = json.dumps(v)
                else:
                    updates[k] = v
        if not updates:
            return self.get_case(case_id, owner)
        updates["updated_at"] = time.time()
        set_clauses = [f"{col} = :{col}" for col in updates.keys()]
        updates["id"] = case_id
        updates["owner"] = owner
        with self.db.begin() as con:
            con.execute(text(f"UPDATE cases SET {', '.join(set_clauses)} WHERE id = :id AND owner = :owner"), updates)
        return self.get_case(case_id, owner)

    def delete_case(self, case_id: str, owner: str) -> bool:
        with self.db.begin() as con:
            # Verify ownership
            row = con.execute(text("SELECT id FROM cases WHERE id = :id AND owner = :owner"), {"id": case_id, "owner": owner}).first()
            if not row:
                return False
            # Cascade delete in transaction to prevent orphaned records
            for tbl in ["case_documents", "case_facts", "evidence_items", "evidence_relationships",
                        "timeline_events", "inconsistencies", "reasoning_rules", "inference_runs",
                        "arguments", "legal_authorities", "saved_analyses"]:
                con.execute(text(f"DELETE FROM {tbl} WHERE case_id = :cid"), {"cid": case_id})
            con.execute(text("DELETE FROM cases WHERE id = :id AND owner = :owner"), {"id": case_id, "owner": owner})
            return True

    # --- Document & Fact Management ---
    def add_document(self, case_id: str, owner: str, filename: str, file_type: str, file_size: int, text_content: str, pages: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        doc_id = "DOC-" + secrets.token_hex(8)
        now = time.time()
        with self.db.begin() as con:
            con.execute(text("""
                INSERT INTO case_documents (id, case_id, owner, filename, file_type, file_size, extracted_text, pages_json, metadata_json, created_at)
                VALUES (:id, :case_id, :owner, :filename, :file_type, :file_size, :extracted_text, :pages_json, :metadata_json, :now)
            """), {
                "id": doc_id,
                "case_id": case_id,
                "owner": owner,
                "filename": filename,
                "file_type": file_type,
                "file_size": file_size,
                "extracted_text": text_content,
                "pages_json": json.dumps(pages),
                "metadata_json": json.dumps(metadata or {}),
                "now": now
            })
            con.execute(text("UPDATE cases SET updated_at = :now WHERE id = :id"), {"now": now, "id": case_id})
        return self.get_document(doc_id, case_id)

    def get_document(self, doc_id: str, case_id: str) -> Optional[Dict[str, Any]]:
        with self.db.connect() as con:
            row = con.execute(text("SELECT * FROM case_documents WHERE id = :id AND case_id = :case_id"), {"id": doc_id, "case_id": case_id}).mappings().first()
            if not row:
                return None
            d = dict(row)
            d["pages"] = json.loads(d.get("pages_json") or "[]")
            d["metadata"] = json.loads(d.get("metadata_json") or "{}")
            return d

    def list_documents(self, case_id: str) -> List[Dict[str, Any]]:
        with self.db.connect() as con:
            rows = con.execute(text("SELECT id, case_id, filename, file_type, file_size, created_at, metadata_json FROM case_documents WHERE case_id = :case_id ORDER BY created_at ASC"), {"case_id": case_id}).mappings().all()
            result = []
            for r in rows:
                d = dict(r)
                d["metadata"] = json.loads(d.get("metadata_json") or "{}")
                result.append(d)
            return result

    def delete_document(self, doc_id: str, case_id: str) -> bool:
        with self.db.begin() as con:
            con.execute(text("DELETE FROM case_facts WHERE document_id = :doc_id"), {"doc_id": doc_id})
            con.execute(text("DELETE FROM timeline_events WHERE document_id = :doc_id"), {"doc_id": doc_id})
            res = con.execute(text("DELETE FROM case_documents WHERE id = :id AND case_id = :case_id"), {"id": doc_id, "case_id": case_id})
            return res.rowcount > 0

    def add_fact(self, case_id: str, document_id: str, text_span: str, entity: str, category: str, fact_type: str, page: Optional[int] = None, span_start: Optional[int] = None, span_end: Optional[int] = None, status: str = "candidate", confidence: Optional[float] = None) -> Dict[str, Any]:
        fact_id = "FACT-" + secrets.token_hex(8)
        now = time.time()
        with self.db.begin() as con:
            con.execute(text("""
                INSERT INTO case_facts (id, case_id, document_id, text, entity, category, fact_type, page, span_start, span_end, status, confidence, created_at)
                VALUES (:id, :case_id, :document_id, :text, :entity, :category, :fact_type, :page, :span_start, :span_end, :status, :confidence, :now)
            """), {
                "id": fact_id,
                "case_id": case_id,
                "document_id": document_id,
                "text": text_span,
                "entity": entity,
                "category": category,
                "fact_type": fact_type,
                "page": page,
                "span_start": span_start,
                "span_end": span_end,
                "status": status,
                "confidence": confidence,
                "now": now
            })
        return self.get_fact(fact_id, case_id)

    def get_fact(self, fact_id: str, case_id: str) -> Optional[Dict[str, Any]]:
        with self.db.connect() as con:
            row = con.execute(text("SELECT * FROM case_facts WHERE id = :id AND case_id = :case_id"), {"id": fact_id, "case_id": case_id}).mappings().first()
            return dict(row) if row else None

    def list_facts(self, case_id: str, category: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.db.connect() as con:
            query = "SELECT f.*, d.filename FROM case_facts f LEFT JOIN case_documents d ON f.document_id = d.id WHERE f.case_id = :case_id"
            params: Dict[str, Any] = {"case_id": case_id}
            if category:
                query += " AND f.category = :category"
                params["category"] = category
            if status:
                query += " AND f.status = :status"
                params["status"] = status
            query += " ORDER BY f.created_at ASC"
            rows = con.execute(text(query), params).mappings().all()
            return [dict(r) for r in rows]

    def update_fact_status(self, fact_id: str, case_id: str, status: str) -> bool:
        with self.db.begin() as con:
            res = con.execute(text("UPDATE case_facts SET status = :status WHERE id = :id AND case_id = :case_id"), {"status": status, "id": fact_id, "case_id": case_id})
            return res.rowcount > 0

    # --- Evidence & Relationships ---
    def add_evidence_item(self, case_id: str, title: str, category: str, description: str, source_doc_id: Optional[str] = None, page: Optional[int] = None, status: str = "verified") -> Dict[str, Any]:
        item_id = "EV-" + secrets.token_hex(6)
        now = time.time()
        with self.db.begin() as con:
            con.execute(text("""
                INSERT INTO evidence_items (id, case_id, title, category, description, source_doc_id, page, status, created_at)
                VALUES (:id, :case_id, :title, :category, :description, :source_doc_id, :page, :status, :now)
            """), {
                "id": item_id,
                "case_id": case_id,
                "title": title,
                "category": category,
                "description": description,
                "source_doc_id": source_doc_id,
                "page": page,
                "status": status,
                "now": now
            })
        return {"id": item_id, "case_id": case_id, "title": title, "category": category, "description": description, "source_doc_id": source_doc_id, "page": page, "status": status, "created_at": now}

    def list_evidence_items(self, case_id: str) -> List[Dict[str, Any]]:
        with self.db.connect() as con:
            rows = con.execute(text("SELECT e.*, d.filename FROM evidence_items e LEFT JOIN case_documents d ON e.source_doc_id = d.id WHERE e.case_id = :case_id ORDER BY e.created_at ASC"), {"case_id": case_id}).mappings().all()
            return [dict(r) for r in rows]

    def add_evidence_relationship(self, case_id: str, source_id: str, target_id: str, relation_type: str, explanation: str, is_suggested: bool = False, is_confirmed: bool = True) -> Dict[str, Any]:
        rel_id = "REL-" + secrets.token_hex(6)
        now = time.time()
        with self.db.begin() as con:
            con.execute(text("""
                INSERT INTO evidence_relationships (id, case_id, source_id, target_id, relation_type, explanation, is_suggested, is_confirmed, created_at)
                VALUES (:id, :case_id, :source_id, :target_id, :relation_type, :explanation, :is_suggested, :is_confirmed, :now)
            """), {
                "id": rel_id,
                "case_id": case_id,
                "source_id": source_id,
                "target_id": target_id,
                "relation_type": relation_type,
                "explanation": explanation,
                "is_suggested": 1 if is_suggested else 0,
                "is_confirmed": 1 if is_confirmed else 0,
                "now": now
            })
        return {"id": rel_id, "case_id": case_id, "source_id": source_id, "target_id": target_id, "relation_type": relation_type, "explanation": explanation, "is_suggested": is_suggested, "is_confirmed": is_confirmed, "created_at": now}

    def list_evidence_relationships(self, case_id: str) -> List[Dict[str, Any]]:
        with self.db.connect() as con:
            rows = con.execute(text("SELECT * FROM evidence_relationships WHERE case_id = :case_id ORDER BY created_at ASC"), {"case_id": case_id}).mappings().all()
            return [dict(r) for r in rows]

    # --- Timeline & Inconsistencies ---
    def add_timeline_event(self, case_id: str, date_str: str, title: str, description: str, document_id: Optional[str] = None, party: str = "", verification_status: str = "verified") -> Dict[str, Any]:
        evt_id = "EVT-" + secrets.token_hex(6)
        now = time.time()
        with self.db.begin() as con:
            con.execute(text("""
                INSERT INTO timeline_events (id, case_id, date_str, title, description, document_id, party, verification_status, created_at)
                VALUES (:id, :case_id, :date_str, :title, :description, :document_id, :party, :verification_status, :now)
            """), {
                "id": evt_id,
                "case_id": case_id,
                "date_str": date_str,
                "title": title,
                "description": description,
                "document_id": document_id,
                "party": party,
                "verification_status": verification_status,
                "now": now
            })
        return {"id": evt_id, "case_id": case_id, "date_str": date_str, "title": title, "description": description, "document_id": document_id, "party": party, "verification_status": verification_status, "created_at": now}

    def list_timeline_events(self, case_id: str) -> List[Dict[str, Any]]:
        with self.db.connect() as con:
            rows = con.execute(text("SELECT t.*, d.filename FROM timeline_events t LEFT JOIN case_documents d ON t.document_id = d.id WHERE t.case_id = :case_id ORDER BY t.date_str ASC, t.created_at ASC"), {"case_id": case_id}).mappings().all()
            return [dict(r) for r in rows]

    def add_inconsistency(self, case_id: str, issue_type: str, title: str, explanation: str, item_a_id: Optional[str] = None, item_b_id: Optional[str] = None, severity: str = "MEDIUM", status: str = "flagged") -> Dict[str, Any]:
        inc_id = "INC-" + secrets.token_hex(6)
        now = time.time()
        with self.db.begin() as con:
            con.execute(text("""
                INSERT INTO inconsistencies (id, case_id, issue_type, title, explanation, item_a_id, item_b_id, status, severity, created_at)
                VALUES (:id, :case_id, :issue_type, :title, :explanation, :item_a_id, :item_b_id, :status, :severity, :now)
            """), {
                "id": inc_id,
                "case_id": case_id,
                "issue_type": issue_type,
                "title": title,
                "explanation": explanation,
                "item_a_id": item_a_id,
                "item_b_id": item_b_id,
                "status": status,
                "severity": severity,
                "now": now
            })
        return {"id": inc_id, "case_id": case_id, "issue_type": issue_type, "title": title, "explanation": explanation, "item_a_id": item_a_id, "item_b_id": item_b_id, "status": status, "severity": severity, "created_at": now}

    def list_inconsistencies(self, case_id: str) -> List[Dict[str, Any]]:
        with self.db.connect() as con:
            rows = con.execute(text("SELECT * FROM inconsistencies WHERE case_id = :case_id ORDER BY created_at DESC"), {"case_id": case_id}).mappings().all()
            return [dict(r) for r in rows]

    def update_inconsistency_status(self, inc_id: str, case_id: str, status: str) -> bool:
        with self.db.begin() as con:
            res = con.execute(text("UPDATE inconsistencies SET status = :status WHERE id = :id AND case_id = :case_id"), {"status": status, "id": inc_id, "case_id": case_id})
            return res.rowcount > 0

    # --- Arguments & Authorities ---
    def add_argument(self, case_id: str, issue_title: str, argument_text: str, supporting_evidence_ids: List[str], assumptions: str = "", counterarguments: str = "", status: str = "proposed") -> Dict[str, Any]:
        arg_id = "ARG-" + secrets.token_hex(6)
        now = time.time()
        with self.db.begin() as con:
            con.execute(text("""
                INSERT INTO arguments (id, case_id, issue_title, argument_text, supporting_evidence_ids, assumptions, counterarguments, status, created_at)
                VALUES (:id, :case_id, :issue_title, :argument_text, :evidence_ids, :assumptions, :counterarguments, :status, :now)
            """), {
                "id": arg_id,
                "case_id": case_id,
                "issue_title": issue_title,
                "argument_text": argument_text,
                "evidence_ids": json.dumps(supporting_evidence_ids),
                "assumptions": assumptions,
                "counterarguments": counterarguments,
                "status": status,
                "now": now
            })
        return {"id": arg_id, "case_id": case_id, "issue_title": issue_title, "argument_text": argument_text, "supporting_evidence_ids": supporting_evidence_ids, "assumptions": assumptions, "counterarguments": counterarguments, "status": status, "created_at": now}

    def list_arguments(self, case_id: str) -> List[Dict[str, Any]]:
        with self.db.connect() as con:
            rows = con.execute(text("SELECT * FROM arguments WHERE case_id = :case_id ORDER BY created_at ASC"), {"case_id": case_id}).mappings().all()
            result = []
            for r in rows:
                item = dict(r)
                item["supporting_evidence_ids"] = json.loads(item.get("supporting_evidence_ids") or "[]")
                result.append(item)
            return result

    def add_authority(self, case_id: str, title: str, citation: str, jurisdiction: str, authority_type: str, url: str = "", notes: str = "", verification_status: str = "verified") -> Dict[str, Any]:
        auth_id = "AUTH-" + secrets.token_hex(6)
        now = time.time()
        with self.db.begin() as con:
            con.execute(text("""
                INSERT INTO legal_authorities (id, case_id, title, citation, jurisdiction, authority_type, url, notes, verification_status, created_at)
                VALUES (:id, :case_id, :title, :citation, :jurisdiction, :authority_type, :url, :notes, :verification_status, :now)
            """), {
                "id": auth_id,
                "case_id": case_id,
                "title": title,
                "citation": citation,
                "jurisdiction": jurisdiction,
                "authority_type": authority_type,
                "url": url,
                "notes": notes,
                "verification_status": verification_status,
                "now": now
            })
        return {"id": auth_id, "case_id": case_id, "title": title, "citation": citation, "jurisdiction": jurisdiction, "authority_type": authority_type, "url": url, "notes": notes, "verification_status": verification_status, "created_at": now}

    def list_authorities(self, case_id: str) -> List[Dict[str, Any]]:
        with self.db.connect() as con:
            rows = con.execute(text("SELECT * FROM legal_authorities WHERE case_id = :case_id ORDER BY created_at ASC"), {"case_id": case_id}).mappings().all()
            return [dict(r) for r in rows]

    # --- Saved Analyses ---
    def save_case_analysis(self, case_id: str, owner: str, analysis_type: str, title: str, data: Dict[str, Any]) -> Dict[str, Any]:
        aid = "ANL-" + secrets.token_hex(8)
        now = time.time()
        with self.db.begin() as con:
            con.execute(text("""
                INSERT INTO saved_analyses (id, case_id, owner, analysis_type, title, data_json, created_at)
                VALUES (:id, :case_id, :owner, :analysis_type, :title, :data_json, :now)
            """), {
                "id": aid,
                "case_id": case_id,
                "owner": owner,
                "analysis_type": analysis_type,
                "title": title,
                "data_json": json.dumps(data),
                "now": now
            })
        return {"id": aid, "case_id": case_id, "analysis_type": analysis_type, "title": title, "data": data, "created_at": now}

    def list_saved_analyses(self, case_id: str, owner: str) -> List[Dict[str, Any]]:
        with self.db.connect() as con:
            rows = con.execute(text("SELECT id, case_id, analysis_type, title, created_at, data_json FROM saved_analyses WHERE case_id = :case_id AND owner = :owner ORDER BY created_at DESC"), {"case_id": case_id, "owner": owner}).mappings().all()
            result = []
            for r in rows:
                item = dict(r)
                item["data"] = json.loads(item.get("data_json") or "{}")
                result.append(item)
            return result
