"""Bounded structural parser. Offsets refer to exact extracted-unit Unicode text."""
import hashlib
import json
import re
import unicodedata
import uuid
from .domain import Clause, DocumentSnapshot, SourceSpan, SourceUnit

MAX_TEXT_CHARACTERS = 1_000_000
MAX_CLAUSES = 2000
HEADING = re.compile(
    r"^\s*(?:#{1,6}\s*)?(?:(?:section|clause|article|பிரிவு|धारा)\s+|§\s*)?"
    r"(?P<label>\d+(?:\.\d+)*(?:\([a-zA-Z]+\))*)(?:[.)])?\s+(?P<title>.+)$",
    re.IGNORECASE,
)
RELATIVE = re.compile(r"^\s*(?:#{1,6}\s*)?\(([a-z])\)\s+(.+)$", re.I)
SCHEDULE = re.compile(r"^\s*(?:#{1,6}\s*)?(Schedule|Annex(?:ure)?|Appendix)\s+([A-Z0-9]+)\b(?:[ :.—-].*)?$", re.I)
MONTHS = re.compile(r"^(?:January|February|March|April|May|June|July|August|September|October|November|December)\b", re.I)

class ExtractedUnits(list):
    """List compatibility for callers of engine.extract; metadata stays attached."""
    def __init__(self, units, *, sha256, media_type, size_bytes, extraction_method, warnings=()):
        super().__init__(units)
        self.metadata = dict(sha256=sha256, hash_basis="original_bytes", media_type=media_type,
                             size_bytes=size_bytes, extraction_method=extraction_method,
                             warnings=list(warnings))

def script_inventory(text):
    scripts = set()
    for char in text:
        if not char.isalpha():
            continue
        name = unicodedata.name(char, "")
        scripts.add("Tamil" if "TAMIL" in name else "Devanagari" if "DEVANAGARI" in name
                    else "Latin" if "LATIN" in name else "Other")
    return sorted(scripts)

def normalize_label(label):
    return "".join(str(unicodedata.digit(c)) if c.isdecimal() else c.lower() for c in label)

def snapshot(pages, name):
    if len(pages) > 20000:
        raise ValueError("Document exceeds the source-unit limit.")
    if sum(len(p["text"]) for p in pages) > MAX_TEXT_CHARACTERS:
        raise ValueError("Extracted text exceeds the 1,000,000-character limit.")
    units = [SourceUnit(id=f"unit-{i+1}", text=p["text"], page=p.get("page"),
                        kind=p.get("kind", "page" if p.get("page") is not None else "text"),
                        location=p.get("location", {})) for i,p in enumerate(pages)]
    canonical = json.dumps([u.model_dump() for u in units], ensure_ascii=False, sort_keys=True).encode("utf-8")
    metadata = getattr(pages, "metadata", None) or dict(
        sha256=hashlib.sha256(canonical).hexdigest(), hash_basis="extracted_units",
        media_type="text/plain", size_bytes=None, extraction_method="provided_text", warnings=[])
    return DocumentSnapshot(id="doc-"+uuid.uuid4().hex, name=name, units=units,
                            scripts=script_inventory("".join(u.text for u in units)), **metadata)

def parent_label(label):
    if label.endswith(")"):
        return label[:label.rfind("(")]
    return label.rsplit(".",1)[0] if "." in label else None

def parse_structure(document):
    clauses=[]; unassigned=[]; warnings=list(document.warnings)
    scope="body"; base=None; current=None; labels={}
    for unit in document.units:
        offset=0
        for line_number, raw in enumerate(unit.text.splitlines(keepends=True), 1):
            line=raw.strip()
            start=offset + len(raw)-len(raw.lstrip())
            end=offset + len(raw.rstrip())
            offset+=len(raw)
            if not line:
                continue
            span=SourceSpan(unit_id=unit.id, start=start, end=end, line=line_number)
            schedule=SCHEDULE.match(line)
            if schedule:
                scope=f"scope-{len(clauses)+1}"
                label=schedule.group(1).lower()+"-"+schedule.group(2).lower()
                title=line; parent=None;base=None
            else:
                match=HEADING.match(line)
                relative=RELATIVE.match(line)
                if match and MONTHS.match(match["title"]):
                    match=None
                if relative and base and relative[1].lower() not in {"i","v","x"}:
                    label=base+"("+relative[1].lower()+")";title=relative[2]
                    parent=parent_label(label)
                elif match:
                    label=normalize_label(match["label"]);title=match["title"]
                    parent=parent_label(label)
                    base=re.sub(r"\(.*","",label)
                else:
                    if relative:
                        warnings.append(f"Unresolved relative numbering at {unit.id}:{line_number}; retained as source text.")
                    if current is None:
                        unassigned.append(span)
                    else:
                        current["spans"].append(span)
                        current["text"]+="\n"+line
                        if unit.page is not None:
                            current["page"]=current["page"] if current["page"] is not None else unit.page
                            current["page_end"]=unit.page
                    continue
            matches=labels.get((scope,parent),[]) if parent else []
            parent_id=matches[0] if len(matches)==1 else None
            if parent and len(matches)!=1:
                warnings.append(f"Parent {parent} for {scope}:{label} is missing or ambiguous.")
            current=dict(id=f"clause-{len(clauses)+1}", document_id=document.id,
                         label=label, title=title, text=line, scope=scope, parent_id=parent_id,
                         spans=[span], page=unit.page, page_end=unit.page)
            clauses.append(current)
            labels.setdefault((scope,label),[]).append(current["id"])
            if len(labels[(scope,label)])>1:
                warnings.append(f"Duplicate clause label {label} in {scope}; references require disambiguation.")
            if len(clauses)>MAX_CLAUSES:
                raise ValueError("This document exceeds the clause limit.")
    if not clauses:
        raise ValueError("No numbered clauses detected. Use a contract with numbered sections; unstructured documents are not yet supported.")
    if unassigned:
        warnings.append("Preamble/source text before the first clause is preserved but not covered by the current reasoning patterns.")
    document.warnings=list(dict.fromkeys(warnings))
    document.coverage="partial" if warnings else "complete"
    return [Clause.model_validate(c) for c in clauses], unassigned
