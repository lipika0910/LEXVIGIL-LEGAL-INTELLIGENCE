# Phase 1 — Requirement and acceptance matrix

Status: draft pending the product decisions in decisions.md. Snapshot: 2026-09-13.

The machine-readable source of truth is requirements.json. This is a full-release capability matrix, not a count of buttons. A partial row can contain working features and passing regression tests while still lacking other acceptance conditions. None of these rows is release-accepted yet.

## Current assessment

59 release-required capabilities: 32 partial and 27 missing against their complete acceptance criteria. This is NOT an implementation-completion percentage. The 25 backend regression cases passed again on 2026-09-13; the two earlier browser workflows were not rerun during this documentation phase.

## Catalogue

| ID | Capability | Baseline | Dependencies |
|---|---|---|---|
| P01 | Three complete workflows | partial | None |
| P02 | Brand and truthful claims | partial | None |
| P03 | Supported scope and limitations | partial | None |
| D01 | PDF/DOCX ingestion | partial | None |
| D02 | Scanned and mixed-page OCR | missing | D01 |
| D03 | Clause hierarchy and location | partial | D01 |
| D04 | Original source viewer | missing | D03, S03 |
| D05 | Safe upload and parsing boundaries | partial | D01 |
| D06 | Document identity and reproducibility | missing | D03 |
| G01 | Explicit and relative references | partial | D03 |
| G02 | Nested terms and aliases | partial | G01 |
| G03 | Amendment precedence and dates | partial | G02 |
| G04 | Exceptions and conditions | missing | G03 |
| G05 | Typed queryable graph | partial | G01, G02, G03, G04 |
| G06 | Obligations and constraint normalization | missing | G05 |
| G07 | Six-pass forward chaining | missing | G06 |
| C01 | Numeric classification | missing | G07 |
| C02 | Temporal classification | partial | G07 |
| C03 | Obligation classification | missing | G07 |
| C04 | Permission classification | missing | G07 |
| C05 | Definition classification | partial | G07 |
| C06 | Scope classification | missing | G07 |
| C07 | Amendment classification | partial | G07 |
| C08 | Exception classification | missing | G07 |
| C09 | Cross-reference classification | partial | G07 |
| C10 | Deontic classification | missing | G07 |
| C11 | Sequence classification | missing | G07 |
| C12 | Condition classification | missing | G07 |
| A01 | Evidence-constrained semantic review | partial | G07 |
| A02 | Task-aware routing and live failure handling | partial | A01 |
| A03 | Long-document dependency context | partial | G05, A01 |
| A04 | Confidence and review states | partial | A01 |
| R01 | Versioned legal-source registry | missing | None |
| R02 | Statutory passage retrieval | partial | R01 |
| R03 | Judgment retrieval and identity | partial | R01 |
| R04 | Citation and proposition verification | missing | R02, R03 |
| R05 | Domain and jurisdiction routing | missing | R04 |
| R06 | Structured dispute analysis | partial | R05 |
| R07 | Document-linked dispute and research | missing | D06, R06 |
| R08 | Independent research and source inspector | partial | R04 |
| U01 | Evidence dashboard and filters | partial | G05, A04 |
| U02 | Complete exports | partial | U01, R08 |
| U03 | Accessible responsive failure states | partial | P01 |
| S01 | Account and session lifecycle | partial | None |
| S02 | Authorization and abuse resistance | partial | S01 |
| S03 | Data lifecycle and deletion | partial | S02 |
| S04 | Secrets, encryption and supply chain | partial | D05, S02 |
| S05 | AI consent and professional-review safeguards | partial | R06, A01 |
| O01 | Durable jobs and cancellation | missing | S03 |
| O02 | Database migrations and backups | partial | S03 |
| O03 | Operational visibility and limits | partial | O01, O02 |
| O04 | Repeatable deployment and rollback | missing | O01, O02, S04 |
| E01 | Labelled benchmark and baselines | missing | G07, A01 |
| E02 | Legal quality and release targets | missing | R04, E01 |
| E03 | Load, fault and security acceptance | missing | O03, O04 |
| E04 | Full demonstration and launch signoff | missing | E02, E03, U02 |
| L01 | English, Tamil and Hindi input support | missing | D03, R06 |
| L02 | Tamil and Hindi OCR evaluation | missing | D02 |
| L03 | Grounded multilingual explanations | missing | A01, R04, L01 |

## Acceptance scenarios

These are test specifications, not claims that automated tests already exist. Each scenario must be implemented and executed, with evidence linked before acceptance.

### AT-P01: Three complete workflows

Source: DOC — ## 16.1 Main dashboard.

Current: Routes exist; research and dispute share an unstructured adapter.

Acceptance: From sign-in run contract, dispute and research; each renders structured evidence and actionable failures.

Existing regression references: `tests/workflows.spec.ts` These only support the subset they exercise.

### AT-P02: Brand and truthful claims

Source: DOC — # 31. Recommended Product Identity.

Current: Supplied logo used; design approval outstanding.

Acceptance: Review desktop/mobile branding; no unsupported accuracy, competitive exclusivity or legal-outcome promises.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-P03: Supported scope and limitations

Source: DOC — ## 5. Scope.

Current: Some coverage notices exist; language and domain policy unapproved.

Acceptance: Approved language/document/domain policy appears before submission and in reports; unsupported inputs do not masquerade as supported.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-D01: PDF/DOCX ingestion

Source: DOC — ## 7.1 Document Ingestion Module.

Current: Text PDFs and DOCX parsed; no OCR or robust complex-layout corpus.

Acceptance: Parse supported PDF/DOCX corpus including tables and schedules; extracted counts and order match annotated fixtures.

Existing regression references: `backend/test_engine.py::test_docx_and_pdf` These only support the subset they exercise.

### AT-D02: Scanned and mixed-page OCR

Source: DOC — ## 7.1 Document Ingestion Module.

Current: Scanned or nearly empty PDF pages reject the complete document.

Acceptance: Run scanned and mixed PDFs; preserve source pages, record OCR quality, distinguish blank pages from unreadable content and expose incomplete coverage.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-D03: Clause hierarchy and location

Source: DOC — ## 7.2 Clause and Section Parser.

Current: Flat numeric clauses and page start/end only.

Acceptance: Reconstruct section/subsection/paragraph hierarchy, tables and annexes; source spans locate exact text; duplicate numbering remains scoped and ambiguous cases stay unresolved.

Existing regression references: `backend/test_engine.py::test_multipage_provenance` These only support the subset they exercise.

### AT-D04: Original source viewer

Source: DOC — ## 16.4 Evidence view.

Current: Extracted text cards, not original-file navigation.

Acceptance: Click finding evidence to open correct PDF page/highlight; DOCX uses honest paragraph/table locations; expired or unauthorized originals cannot be read.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-D05: Safe upload and parsing boundaries

Source: DOC — # 15. Privacy and Security.

Current: Extension/signature/size checks exist; multipart spooling and resource limits need audit.

Acceptance: Test signature mismatch, malformed archives, zip bombs, encrypted files, chunked oversize requests and parser timeouts; reject safely and clean temporary data.

Existing regression references: `backend/test_engine.py::test_invalid_uploads` These only support the subset they exercise.

### AT-D06: Document identity and reproducibility

Source: DOC — # 26. Privacy Model.

Current: No source hash, parser version or full provenance envelope.

Acceptance: Store owner, input hash, created time, expiry, parser/rule versions and analysis date; identical input/version reproduces deterministic facts.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-G01: Explicit and relative references

Source: DOC — ## 7.3 Cross-Reference Resolver.

Current: Basic section/clause regex; no aliases, ranges or robust relative resolution.

Acceptance: Resolve Section 4.2, §4.2, Clause 7(b), ranges, this Section and heading aliases; preserve raw expression and alternatives instead of guessing.

Existing regression references: `backend/test_engine.py::test_missing_reference` These only support the subset they exercise.

### AT-G02: Nested terms and aliases

Source: DOC — ## 7.4 Defined-Term Resolver.

Current: Quoted means definitions and substring usage links.

Acceptance: Resolve alias chains and imported definitions; detect cycles, shadowing and scope; explain paths without collapsing unlike terms.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-G03: Amendment precedence and dates

Source: DOC — ## 7.5 Amendment and Precedence Resolver.

Current: Limited day-value amendments; ambiguity warnings.

Acceptance: Apply explicit scoped amendments by effective date and precedence rather than text order; preserve old values and provenance; unresolved activation must not become active.

Existing regression references: `backend/test_engine.py::test_future_amendment`, `backend/test_engine.py::test_ambiguous_effective_condition_not_applied` These only support the subset they exercise.

### AT-G04: Exceptions and conditions

Source: DOC — ## 7.6 Exception Resolver.

Current: One negative-control test; no general exception representation.

Acceptance: Represent except/notwithstanding/unless/subject-to edges and activation conditions; ordinary conditional exceptions do not become contradictory simultaneous duties.

Existing regression references: `backend/test_engine.py::test_clean_exception_not_conflict` These only support the subset they exercise.

### AT-G05: Typed queryable graph

Source: DOC — ## 7.7 Contract Knowledge Graph.

Current: Reference list and definition records, not full typed graph.

Acceptance: All declared node/edge types validate; graph queries return adjacency and actual dependency paths; no dangling IDs or invented sequential evidence paths.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-G06: Obligations and constraint normalization

Source: DOC — ## 7.8 Obligation and Condition Extraction.

Current: Duration regex only; no normalized obligation facts.

Acceptance: Extract actor/modality/action/object/condition with spans; normalize amounts, units, currencies, dates, percentages and ranges without equating unlike scopes or calendar/business days.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-G07: Six-pass forward chaining

Source: DOC — # 9. Inference Engine.

Current: Procedural pattern loops; no general fact/rule engine.

Acceptance: Run structural, reference, amendment, effective-obligation, conflict and evidence passes to fixed point; version rules, bound iterations, deduplicate facts and retain derivation IDs.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-C01: Numeric classification

Source: DOC — # 8. Contradiction Taxonomy.

Current: Enum/prompt membership exists; full class-specific deterministic coverage is not demonstrated.

Acceptance: On approved positive fixtures detect different liability caps under the same currency, event and scope; on negative fixtures show that currency or scope differences alone are not conflicts. Assert category, evidence, activation state and explanation. Report class precision/recall on held-out data.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-C02: Temporal classification

Source: DOC — # 8. Contradiction Taxonomy.

Current: Enum/prompt membership exists; full class-specific deterministic coverage is not demonstrated.

Acceptance: On approved positive fixtures detect a late-payment trigger precedes the amended due date; on negative fixtures show that different trigger events or business/calendar units require resolution. Assert category, evidence, activation state and explanation. Report class precision/recall on held-out data.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-C03: Obligation classification

Source: DOC — # 8. Contradiction Taxonomy.

Current: Enum/prompt membership exists; full class-specific deterministic coverage is not demonstrated.

Acceptance: On approved positive fixtures detect incompatible mandatory actions for the same actor and condition; on negative fixtures show that different actors or nonoverlapping conditions are not conflicts. Assert category, evidence, activation state and explanation. Report class precision/recall on held-out data.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-C04: Permission classification

Source: DOC — # 8. Contradiction Taxonomy.

Current: Enum/prompt membership exists; full class-specific deterministic coverage is not demonstrated.

Acceptance: On approved positive fixtures detect permission and prohibition of the same act under the same condition; on negative fixtures show that scoped exceptions reconcile the apparent mismatch. Assert category, evidence, activation state and explanation. Report class precision/recall on held-out data.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-C05: Definition classification

Source: DOC — # 8. Contradiction Taxonomy.

Current: Enum/prompt membership exists; full class-specific deterministic coverage is not demonstrated.

Acceptance: On approved positive fixtures detect incompatible active meanings of one term in the same scope; on negative fixtures show that explicit supersession is an update, not inherently a conflict. Assert category, evidence, activation state and explanation. Report class precision/recall on held-out data.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-C06: Scope classification

Source: DOC — # 8. Contradiction Taxonomy.

Current: Enum/prompt membership exists; full class-specific deterministic coverage is not demonstrated.

Acceptance: On approved positive fixtures detect overlapping incompatible applicability rules; on negative fixtures show that general and specific rules may coexist. Assert category, evidence, activation state and explanation. Report class precision/recall on held-out data.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-C07: Amendment classification

Source: DOC — # 8. Contradiction Taxonomy.

Current: Enum/prompt membership exists; full class-specific deterministic coverage is not demonstrated.

Acceptance: On approved positive fixtures detect an amendment leaves an incompatible dependent obligation; on negative fixtures show that replacement of the old term alone is not a contradiction. Assert category, evidence, activation state and explanation. Report class precision/recall on held-out data.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-C08: Exception classification

Source: DOC — # 8. Contradiction Taxonomy.

Current: Enum/prompt membership exists; full class-specific deterministic coverage is not demonstrated.

Acceptance: On approved positive fixtures detect exception and general rule remain incompatible after precedence resolution; on negative fixtures show that a valid active exception narrows the general rule. Assert category, evidence, activation state and explanation. Report class precision/recall on held-out data.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-C09: Cross-reference classification

Source: DOC — # 8. Contradiction Taxonomy.

Current: Enum/prompt membership exists; full class-specific deterministic coverage is not demonstrated.

Acceptance: On approved positive fixtures detect a target is missing or semantically misdirected; on negative fixtures show that existence of a target alone does not prove relevance. Assert category, evidence, activation state and explanation. Report class precision/recall on held-out data.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-C10: Deontic classification

Source: DOC — # 8. Contradiction Taxonomy.

Current: Enum/prompt membership exists; full class-specific deterministic coverage is not demonstrated.

Acceptance: On approved positive fixtures detect incompatible modalities on the same normalized proposition; on negative fixtures show that SHALL and MAY are not automatically contradictory. Assert category, evidence, activation state and explanation. Report class precision/recall on held-out data.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-C11: Sequence classification

Source: DOC — # 8. Contradiction Taxonomy.

Current: Enum/prompt membership exists; full class-specific deterministic coverage is not demonstrated.

Acceptance: On approved positive fixtures detect mutually incompatible event ordering constraints; on negative fixtures show that unrelated event sequences remain independent. Assert category, evidence, activation state and explanation. Report class precision/recall on held-out data.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-C12: Condition classification

Source: DOC — # 8. Contradiction Taxonomy.

Current: Enum/prompt membership exists; full class-specific deterministic coverage is not demonstrated.

Acceptance: On approved positive fixtures detect incompatible activation constraints in overlapping scope; on negative fixtures show that mutually exclusive scenarios are not automatically conflicts. Assert category, evidence, activation state and explanation. Report class precision/recall on held-out data.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-A01: Evidence-constrained semantic review

Source: DOC — ## 11.3 LLM verifier contract.

Current: Structured output, quote/ID validation and opt-in report copy exist.

Acceptance: Assess every candidate exactly once; invalid IDs/quotes, refusals and truncation fail closed; model output never silently overwrites deterministic facts.

Existing regression references: `backend/test_verification.py::test_fabricated_quote_rejected`, `backend/test_verification.py::test_duplicate_assessment_rejected`, `backend/test_verification.py::test_mocked_refusal_fails_closed` These only support the subset they exercise.

### AT-A02: Task-aware routing and live failure handling

Source: HTML — Slide 6 of 7.

Current: All reviews start at Luna and escalate only on UNCERTAIN; differs from task-aware source plan.

Acceptance: Routine normalization, normal verification and high-risk ambiguity follow approved routing; test actual model access, outage, rate-limit, incomplete response and cost cap with no silent paid retry loop.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-A03: Long-document dependency context

Source: DOC — ## 11.3 LLM verifier contract.

Current: 120,000-character whole-report cap; no dependency-aware context assembly.

Acceptance: Assemble candidate dependency closure with provenance; handle long inputs without dropping relevant amendments; oversized context is explicit and coverage remains accurate.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-A04: Confidence and review states

Source: DOC — # 24. Safety and Reliability Requirements.

Current: No uncalibrated percentage; AI verdict separate, summary still counts explained items.

Acceptance: Separate candidates, model-supported, explained-away and unresolved totals; show calibration only when measured, and always distinguish legal professional review.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-R01: Versioned legal-source registry

Source: DOC — ## 12.1 Source priority.

Current: Static allowlist of three domains only.

Acceptance: Register source type, authority, jurisdiction, versions, licence/access rules and refresh policy; a registry update does not require rewriting the reasoning engine.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-R02: Statutory passage retrieval

Source: DOC — ## 12.2 Statutory retrieval.

Current: Provider web-search adapter without versioned statute records.

Acceptance: Return Act/section/subsection, relevant passage, URL and effective/amendment dates as of the issue date; unknown dates are explicit.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-R03: Judgment retrieval and identity

Source: DOC — ## 12.3 Case-law retrieval.

Current: Official-domain search, no dedicated case metadata verifier.

Acceptance: Confirm case name, court, date, identifiers and paragraph evidence; ambiguous identities are not verified; unavailable/CAPTCHA-protected sources produce honest limitations.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-R04: Citation and proposition verification

Source: DOC — # 25. Citation Integrity Policy.

Current: RETRIEVED labels, not source or proposition verification.

Acceptance: Every material legal proposition maps to a retrieved passage; evaluate identity, text match, currency and applicability separately; fabricated citations fail; VERIFIED never means outcome guaranteed.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-R05: Domain and jurisdiction routing

Source: DOC — ## 6. Legal-Domain Coverage Strategy.

Current: Shared prompt and free-text location fields.

Acceptance: For Criminal, Civil procedure, Contracts, Consumer, Property, Family, Labour and Cyber/IT, use approved source coverage and issue dates; uncertain forum/law questions request missing facts instead of assuming from state alone.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-R06: Structured dispute analysis

Source: DOC — # 13. Dispute Analysis Workflow.

Current: Description/state/district form and unstructured answer.

Acceptance: Separate supplied facts, assumptions, issues, authorities, procedural considerations, evidence checklist, unresolved questions and high-stakes review triggers; validate each claim-to-source link.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-R07: Document-linked dispute and research

Source: DOC — # 13. Dispute Analysis Workflow.

Current: No optional document linkage in dispute API.

Acceptance: Attach authorized documents/analyses to a dispute or question; combine contract evidence with legal-source evidence without cross-owner leakage.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-R08: Independent research and source inspector

Source: DOC — ## 16.5 Legal research report.

Current: Query form and source links; plain answer body.

Acceptance: Render structured research with per-proposition source navigation, verification reasons, timestamps and unsupported-claim handling.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-U01: Evidence dashboard and filters

Source: DOC — ## 16.3 Conflict list.

Current: Stats, filters, source cards and relationship lists exist.

Acceptance: Filters, categories, semantic verdicts and severity counts agree; no stale selected finding under empty filter; inspect actual graph paths and clauses side by side.

Existing regression references: `tests/workflows.spec.ts` These only support the subset they exercise.

### AT-U02: Complete exports

Source: DOC — # 15. Privacy and Security.

Current: JSON and printable clauses/findings; print omits graph/terms and provenance versions.

Acceptance: All workflow exports preserve findings, graph paths, facts, sources, verification, uncertainty, analysis/version dates and disclaimers with readable pagination.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-U03: Accessible responsive failure states

Source: DOC — # 16. User Interface.

Current: Desktop and 390px browser checks; broader audit missing.

Acceptance: Keyboard-only upload/review/delete, focus restoration, screen-reader labels, readable contrast, expired sessions, empty/error states and supported browsers pass.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-S01: Account and session lifecycle

Source: DOC — # 15. Privacy and Security.

Current: Password login/registration and HTTP-only sessions; no recovery or email verification.

Acceptance: Verify email, reset password with expiring single-use token, revoke sessions and enforce safe account changes without leaking secrets.

Existing regression references: `backend/test_api.py::test_auth_validation` These only support the subset they exercise.

### AT-S02: Authorization and abuse resistance

Source: DOC — # 15. Privacy and Security.

Current: Owner filters and local rate limits; no distributed enforcement.

Acceptance: Cross-owner access fails for reports, jobs, originals and exports; shared limits hold across workers; CSRF, object-ID tampering and concurrent admission tested.

Existing regression references: `backend/test_api.py::test_owner_isolation_and_delete`, `backend/test_api.py::test_expiry_and_csrf` These only support the subset they exercise.

### AT-S03: Data lifecycle and deletion

Source: DOC — # 26. Privacy Model.

Current: 24-hour report expiry and sign-out deletion; original-file policy undecided.

Acceptance: Approved consent/retention applies to originals, parsed data, queues, caches and backups; expired data cannot be read; deletion during work cannot recreate it.

Existing regression references: `backend/test_api.py::test_save_logout_retention` These only support the subset they exercise.

### AT-S04: Secrets, encryption and supply chain

Source: DOC — # 15. Privacy and Security.

Current: Server key boundary and a few headers; host controls unconfigured.

Acceptance: No secrets in bundle/logs; HTTPS and storage encryption configured; scanner finds no unaccepted critical/high issues; uploads and third-party fetches have bounded isolation.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-S05: AI consent and professional-review safeguards

Source: DOC — # 24. Safety and Reliability Requirements.

Current: Contract AI dialog and research disclosure; high-risk path not structured.

Acceptance: Consent is recorded before transmission; provider retention disclosures accurate; configured high-risk cases surface professional-review triggers without guarantees.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-O01: Durable jobs and cancellation

Source: DOC — # 24. Safety and Reliability Requirements.

Current: In-memory thread pool; startup marks all unfinished rows failed.

Acceptance: Persist safe job inputs under approved retention; lease jobs atomically, retry idempotently, cancel, recover crashes and avoid duplicate charges/results across two workers.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-O02: Database migrations and backups

Source: DOC — # 20. Technology Stack.

Current: SQLite local and PostgreSQL URL support; CREATE TABLE on import.

Acceptance: Version migrations, test PostgreSQL behaviour, restore backup and rollback deploy without losing authorized saved records.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-O03: Operational visibility and limits

Source: DOC — ### System.

Current: Basic health bool and sparse logs; no provider probe or service metrics.

Acceptance: Readiness checks dependencies separately; monitor latency, queue age, failures and costs without sensitive text; set owner and global budgets and tested alerts.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-O04: Repeatable deployment and rollback

Source: DOC — ## Deployment.

Current: Local scripts only; deployment target not approved.

Acceptance: Locked reproducible builds, staging/production secrets, SPA/API routing, TLS, health checks, startup lifecycle and rollback validated on chosen host.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-E01: Labelled benchmark and baselines

Source: DOC — # 23. Evaluation Methodology.

Current: Small synthetic regression suite; no 30–60-contract benchmark.

Acceptance: Build 30–60 controlled contracts with all twelve classes, negative controls and document-family holdouts; compare rule-only, LLM-only and hybrid on identical inputs.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-E02: Legal quality and release targets

Source: DOC — ### Legal research.

Current: No legal-reviewed source evaluation or approved quality thresholds.

Acceptance: Approved reviewer adjudicates source identity/support/currency/applicability by domain; report precision, recall and unsupported claims separately; targets approved before held-out results.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-E03: Load, fault and security acceptance

Source: DOC — # 24. Safety and Reliability Requirements.

Current: Local regression tests only.

Acceptance: On staging, run approved workload and timeout, provider outage, crash, cancellation, expiry, restore and security tests; document unresolved risk and owners.

Existing regression references: None mapped. These only support the subset they exercise.

### AT-E04: Full demonstration and launch signoff

Source: DOC — # 28. Final Demonstration Scenario.

Current: Synthetic six-clause sample; no full demonstration or deployment evidence.

Acceptance: Use a 30–50 page annotated fictional agreement and related dispute/research; complete all 14 source-demo steps with computed results, export/delete proof and human release approval.

Existing regression references: None mapped. These only support the subset they exercise.


### AT-L01: English, Tamil and Hindi input support

Source: DOC — ## 11.1 Role of the LLM; user confirmation Q01.

Current: No language-specific parsing, OCR or explanation evaluation is implemented.

Acceptance: Upload and query in each approved language and representative mixed-language text; preserve Unicode and original source spans; language detection and unsupported-input messages are accurate.

Existing regression references: None mapped.

### AT-L02: Tamil and Hindi OCR evaluation

Source: DOC — ## 7.1 Document Ingestion Module; user confirmation Q01.

Current: No language-specific parsing, OCR or explanation evaluation is implemented.

Acceptance: Evaluate Tamil and Devanagari printed scans, including mixed English passages; report extraction quality per language/page, preserve original images and never silently substitute unreliable OCR text.

Existing regression references: None mapped.

### AT-L03: Grounded multilingual explanations

Source: DOC — ## 11.1 Role of the LLM; user confirmation Q01.

Current: No language-specific parsing, OCR or explanation evaluation is implemented.

Acceptance: Explain results in English, Tamil and Hindi while preserving quoted source language, names, citations, numbers and modality; label translations and evaluate semantic fidelity with competent reviewers.

Existing regression references: None mapped.

## Change discipline

Keep stable IDs. When changing scope, record the user decision and update both the catalogue and JSON. Add new requirements rather than silently removing a hard one. The read-only validator checks source fingerprints, links, dependencies and catalogue consistency. It does not evaluate software correctness or legal quality.
