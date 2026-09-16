# G1 implementation checkpoint — 2026-09-13

Status: implemented and locally verified **foundation slice**, not full G1 acceptance or production approval.

The Phase 1 requirements matrix remains the original gap snapshot. This checkpoint records newer implementation evidence; it does not mark requirements accepted or resolve pending product decisions.

## Delivered

- `backend/domain.py`: versioned contract-report schema (`1.0`), document identity, original-byte or extracted-unit SHA-256 with explicit hash basis, parser/rule versions, typed clauses and exact source spans.
- Evidence validation rejects altered quotes, invalid offsets/line numbers, missing source units, cross-document clauses, invalid/cyclic hierarchy, overlapping spans, omitted non-whitespace extracted text, unknown finding evidence and inconsistent summary counts.
- `backend/ingestion.py`: bounded PDF/DOCX/UTF-8 extraction. PDF page locations are retained; DOCX paragraphs/table cells carry structural locations, not invented page numbers. Truly blank PDF pages are distinguished from pages needing OCR. Archive, file, page, unit and text bounds apply.
- `backend/structure.py`: nested numbered clauses, absolute parenthetical subclauses, schedule scope, Unicode decimal normalization and source-preserving treatment of ambiguous numbering/preamble. Warnings remain visible in report limitations.
- English, Tamil and Hindi fixture text is preserved through parsing and API save/reload. Script detection is not language identification or proof of legal-analysis quality.
- Contract jobs validate new versioned results before persistence. Existing UI fields and legacy saved-report reads remain compatible.

## Local verification

Environment: Windows, Python virtual environment, SQLite test database; Chrome against local Vite and FastAPI development servers.

| Command | Result |
|---|---|
| `.venv\Scripts\python.exe -m pytest backend -q` | 50 passed; two test-client dependency deprecation warnings |
| `npm run build` | TypeScript and Vite production bundle passed |
| `npm run test:e2e` | 2 Chrome workflows passed |

Browser coverage: account creation, sample and actual upload, versioned persisted report, source/reference views, saving, JSON download initiation, deletion, unauthenticated access rejection, print content, invalid-PDF error, mobile navigation and horizontal-overflow check. The mobile screenshot was visually inspected. Screenshots/traces are kept outside the repository. This is not exhaustive accessibility, cross-browser, load or security certification.

## Remaining before G1 closure

- OCR for English/Tamil/Hindi with measured extraction quality and page/coordinate provenance.
- Explicit original-retention consent, approved TTL, encrypted private original storage, authorized viewer/highlights, automatic deletion and deletion verification. Saving a report must not silently extend original retention.
- Stronger hierarchy/list/table/layout fixtures, DOCX automatic numbering, ambiguous relative Roman numbering and duplicate/scope resolution.
- Benchmark annotations and approved workload/quality limits; source spans currently address extracted text, not all original-page bounding boxes.
- Broader typed contracts for normalized legal facts, graph derivations and independently verified authorities in subsequent gates.

Current deterministic semantics remain primarily English and limited to the disclosed patterns. Preserving Tamil/Hindi text does not make Tamil/Hindi legal reasoning complete. No live AI, legal-source validation, external deployment, storage provisioning or production data migration was performed in this checkpoint.

## Next build slice

Implement the consent/retention lifecycle and source-access boundary with configurable policy and fault tests, then connect OCR behind explicit capability checks. Resolve actual retention duration and hosting/data-residency choices before enabling production original storage. Continue the G2 reasoning work only with clear source evidence and scoped coverage.
