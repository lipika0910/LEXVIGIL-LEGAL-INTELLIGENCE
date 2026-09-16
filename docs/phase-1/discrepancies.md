# Discrepancy register

Observed on 2026-09-13. This register describes remaining work; it does not silently amend the supplied plan.

| ID | Source versus implementation / source conflict | Required disposition |
|---|---|---|
| X01 | DOC §§7–10 and HTML Slide 5 require graph facts and six-pass forward chaining. backend/engine.py has bounded regex/pattern loops. | Implement typed graph, normalized facts, precedence and fixed-point reasoning (G01–G07); do not label it complete symbolic reasoning now. |
| X02 | Twelve classes are listed in prompts/enums, but deterministic coverage is limited to payment, definitions, amendment warnings and broken references. | Separate per-class positive/negative acceptance and benchmark (C01–C12). |
| X03 | HTML architecture shows Luna→Terra→Astra; detailed Slide 6/DOC §11 assigns routine normalization to Luna and normal verification to Terra. Current verifier starts every review at Luna and stops unless UNCERTAIN. | Resolve Q09; use task/risk-aware routing, not merely a fallback list. |
| X04 | Source verifier input is dependency-scoped; current verifier sends the full report up to 120,000 characters. | Implement dependency closure and explicit context coverage without losing distant amendments (A03). |
| X05 | DOC §22 shows file_id/full-mode request and named source/research endpoints. Current upload is multipart returning 202/id; no /api/sources/verify or /api/rules/count. | Define versioned public contract and compatibility; implement source verification and rule diagnostics; document intentional async response. |
| X06 | DOC §18 describes typed domain objects; current report dictionaries/JSON text are largely unvalidated and persistence is ad-hoc SQL. | Introduce shared domain schemas, report versions, migrations and PostgreSQL tests (D06/G05/O02). |
| X07 | Source shows original clauses/page navigation; UI currently shows extracted-text cards only. | Original viewer and location mapping depend on approved original-retention policy (D04/Q02). |
| X08 | UI/README say original upload bytes are processed in memory. Multipart infrastructure can spool before file.read; no spool audit exists. | Treat memory-only claim as unverified; inspect multipart/temp behaviour and enforce approved cleanup/storage policy before privacy signoff (D05/S03). |
| X09 | Source has nested definitions and condition-aware exceptions. A clean-exception regression does not implement an exception engine. | Positive and negative condition/precedence tests plus explicit relations (G02/G04). |
| X10 | Current evidence IDs are collected lists and displayed sequentially; reference totals mix term-use and explicit links. | Display actual directed derivations and separately define counts; do not imply every adjacent ID is a graph edge (G05/U01). |
| X11 | Source requires retrieved, validated passages before summarization. Current research relies on provider annotations/domain checks and plain answer text. | Versioned registry, source identity and proposition-to-passage checks; RETRIEVED is not VERIFIED (R01–R08). |
| X12 | DOC source state adds OUTDATED to VERIFIED/UNVERIFIED/FAILED. Source retrieval, textual match, currency and applicability are distinct. | Store separate checks and reasons; render aggregate label only with its defined scope (R04). |
| X13 | Dispute document attachments and related-contract research are specified but absent from the current form/API. | Add authorized document linkage, source merging and structured outputs (R07). |
| X14 | HTML uses fixed 154 clauses, 71 refs, 94% confidence and exclusivity/90% claims; some examples select a forum without sufficient facts. | Keep them illustrative/unverified; derive counts, calibrate confidence and retrieve/validate jurisdiction evidence. Never encode sample legal conclusions as rules. |
| X15 | Current AI-explained candidates remain in the same potential-finding count. | Preserve audit history but separate actionable, explained and unresolved totals and exports (A04/U01). |
| X16 | Printable report omits full relationships/terms and version metadata; source calls for exported evidence trail. | Unified structured reports and complete export acceptance (U02). |
| X17 | Source suggests encrypted temporary originals; current code stores extracted text/report rows and uses thread-memory work inputs. | Q02/Q08 plus deletion covering jobs, originals, derived data and backups; no persistent object storage until approved. |
| X18 | Startup marks every queued/processing row failed; in-memory counters and thread pool do not coordinate replicas. | Durable leased jobs, shared admission limits and idempotency before multiple workers (O01/S02). |
| X19 | API health reports configured based only on key presence. | Separate liveness, dependency readiness, provider configuration and actually verified access (O03). |
| X20 | Source suggests Tailwind/Axios and folder layout; code uses CSS/fetch and different folders. | Proposed intentional implementation variation: keep working libraries, meet behaviour/accessibility requirements; no cosmetic rewrite required. |
| X21 | Source's 30-day roadmap is an illustrative sequence, not a delivery guarantee. | Use acceptance gates; estimate only after scope, hosting, workload and reviewer availability are known. |
| X22 | 25 regression cases and two browser flows are not the 30–60-contract benchmark or live research validation. | Retain them as subset evidence; create family-held-out evaluation, legal review, staging/fault/load checks (E01–E04). |

## Verification hygiene

- test_expiry_and_csrf calls cleanup directly; it does not establish timed background sweeping across a production outage.
- test_real_upload_and_failure verifies a queued response for one bad text input; the separate browser test checks a terminal invalid-PDF failure.
- Provider escalation/refusal tests use mocks. They prove adapter behaviour for those mocks, not provider/model availability or legal correctness.
- Source document integrity hashes freeze the baseline inputs, not the truth of claims inside them.

## Confirmed scope additions

Q01 confirms English, Tamil and Hindi (L01–L03); each language requires input, OCR and semantic-quality evidence. Q02 confirms temporary originals with explicit consent and automatic deletion. References to Q02 above now mean implementing that confirmed policy, while Q08 still controls saved-original and backup retention details.
