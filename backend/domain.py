"""Versioned contract output and source provenance; compatible with existing UI keys."""
from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

PARSER_VERSION = "structure-0.2.0"
RULE_VERSION = "patterns-0.1.0"

class Record(BaseModel):
    model_config = ConfigDict(extra="forbid")

class SourceUnit(Record):
    id: str
    text: str
    page: int | None = Field(default=None, ge=1)
    kind: Literal["page", "text", "paragraph", "table_cell"]
    location: dict[str, int] = Field(default_factory=dict)

class SourceSpan(Record):
    unit_id: str
    start: int = Field(ge=0)
    end: int = Field(gt=0)
    line: int = Field(ge=1)

    @model_validator(mode="after")
    def ordered(self):
        if self.end <= self.start:
            raise ValueError("Source span must have positive length.")
        return self

class DocumentSnapshot(Record):
    id: str
    name: str
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    hash_basis: Literal["original_bytes", "extracted_units"]
    media_type: str
    size_bytes: int | None = Field(default=None, ge=0)
    parser_version: str = PARSER_VERSION
    extraction_method: Literal["provided_text", "pdf_text", "pdf_ocr_mixed", "docx_text", "utf8_text"]
    scripts: list[str] = Field(default_factory=list)
    units: list[SourceUnit]
    warnings: list[str] = Field(default_factory=list)
    coverage: Literal["complete", "partial"] = "complete"

    @model_validator(mode="after")
    def unique_units(self):
        if len({u.id for u in self.units}) != len(self.units):
            raise ValueError("Duplicate source unit ID.")
        return self

class Clause(Record):
    id: str
    document_id: str
    label: str
    title: str
    text: str
    scope: str = "body"
    parent_id: str | None = None
    spans: list[SourceSpan] = Field(min_length=1)
    page: int | None = None
    page_end: int | None = None

class Reference(Record):
    source: str
    target: str | None
    label: str
    type: Literal["references", "uses", "amends"]
    status: Literal["RESOLVED", "UNRESOLVED"]

class Definition(Record):
    term: str
    value: str
    source: str
    effective_value: str
    amendment: str | None

class Amendment(Record):
    source: str
    target: str
    value: str
    active: bool
    effective_date: str | None

class Finding(Record):
    id: str
    category: Literal["Numeric","Temporal","Obligation","Permission","Definition","Scope","Amendment","Exception","Cross-reference","Deontic","Sequence","Condition"]
    title: str
    severity: Literal["LOW", "MEDIUM", "HIGH"]
    explanation: str
    evidence: list[str] = Field(min_length=1)
    review_required: bool
    verification: str
    confidence: float | None = Field(default=None, ge=0, le=1)
    semantic: dict | None = None

class ContractReport(Record):
    schema_version: Literal["1.0"] = "1.0"
    kind: Literal["contract"]
    title: str
    as_of: date
    rule_version: str = RULE_VERSION
    document: DocumentSnapshot
    clauses: list[Clause]
    unassigned_spans: list[SourceSpan] = Field(default_factory=list)
    references: list[Reference]
    definitions: list[Definition]
    amendments: list[Amendment]
    findings: list[Finding]
    summary: dict[str, int]
    limitations: list[str]
    verification: str
    semantic_review: dict | None = None

    @model_validator(mode="after")
    def integrity(self):
        units = {u.id: u for u in self.document.units}
        clauses = {c.id: c for c in self.clauses}
        covered = {u.id: [] for u in self.document.units}
        if len(clauses) != len(self.clauses):
            raise ValueError("Duplicate clause ID.")
        def read_span(span):
            unit = units.get(span.unit_id)
            if unit is None or span.end > len(unit.text):
                raise ValueError("Source span is outside its source unit.")
            prefix = unit.text[:span.start]
            line = len(prefix.splitlines()) + (1 if not prefix or prefix.endswith(("\n", "\r", "\v", "\f", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029")) else 0)
            if span.line != line:
                raise ValueError("Source line number does not match its offset.")
            covered[span.unit_id].append((span.start, span.end))
            return unit.text[span.start:span.end]
        for span in self.unassigned_spans:
            read_span(span)
        for clause in self.clauses:
            if clause.document_id != self.document.id:
                raise ValueError("Clause belongs to a different document.")
            if clause.text != "\n".join(read_span(s) for s in clause.spans):
                raise ValueError("Clause text differs from its source spans.")
            parent = clause.parent_id
            seen = {clause.id}
            while parent is not None:
                if parent not in clauses or parent in seen:
                    raise ValueError("Clause hierarchy is invalid or cyclic.")
                if clauses[parent].scope != clause.scope:
                    raise ValueError("Clause parent belongs to a different scope.")
                seen.add(parent)
                parent = clauses[parent].parent_id
            pages = [units[s.unit_id].page for s in clause.spans if units[s.unit_id].page is not None]
            if (clause.page, clause.page_end) != ((pages[0], pages[-1]) if pages else (None, None)):
                raise ValueError("Clause page provenance is inconsistent.")
        for uid, ranges in covered.items():
            cursor = 0
            for start, end in sorted(ranges):
                if start < cursor:
                    raise ValueError("Source spans overlap or are duplicated.")
                if units[uid].text[cursor:start].strip():
                    raise ValueError("Extracted source text was silently omitted.")
                cursor = end
            if units[uid].text[cursor:].strip():
                raise ValueError("Extracted source text was silently omitted.")
        for ref in self.references:
            if ref.source not in clauses or (ref.target is not None and ref.target not in clauses):
                raise ValueError("Reference contains an unknown clause.")
            if (ref.status == "RESOLVED") != (ref.target is not None):
                raise ValueError("Reference state and target disagree.")
        for definition in self.definitions:
            if definition.source not in clauses or (definition.amendment is not None and definition.amendment not in clauses):
                raise ValueError("Definition contains an unknown clause.")
        for amendment in self.amendments:
            if amendment.source not in clauses or amendment.target not in clauses:
                raise ValueError("Amendment contains an unknown clause.")
        if len({f.id for f in self.findings}) != len(self.findings):
            raise ValueError("Duplicate finding ID.")
        for finding in self.findings:
            if not set(finding.evidence) <= clauses.keys():
                raise ValueError("Finding contains an unknown evidence ID.")
        expected = dict(clauses=len(self.clauses), references=len(self.references),
                        resolved=sum(r.status == "RESOLVED" for r in self.references),
                        definitions=len(self.definitions), amendments=len(self.amendments),
                        conflicts=len(self.findings))
        if self.summary != expected:
            raise ValueError("Summary does not match the report contents.")
        return self

def validate_contract_report(value):
    result = ContractReport.model_validate(value).model_dump(mode="json")
    # Preserve the legacy distinction between no review and a review result.
    if result["semantic_review"] is None:
        result.pop("semantic_review")
    for finding in result["findings"]:
        if finding["semantic"] is None:
            finding.pop("semantic")
    return result
