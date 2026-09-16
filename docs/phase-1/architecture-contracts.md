# Proposed architecture and contracts

These are Phase 1 design contracts, not implemented APIs. Exact providers, storage and limits remain subject to decisions.md.

## Service boundaries

Keep a modular application rather than a large agent framework:
API/auth → authorized job submission → durable worker → ingestion → typed structure → resolvers → graph/facts → rules/constraints → evidence candidates → optional semantic review → versioned report.
Dispute/research branches use fact/issue routing → authorized source adapters → source/passage verification → supported claim assembly. Shared evidence and report schemas join the branches.

Do not let an LLM instruction substitute for a source verifier or graph rule.

## Canonical objects

| Object | Required contract |
|---|---|
| Document | Opaque ID, owner, content hash, media type, size, language/quality status, retention policy, creation/expiry and ingestion version; original storage reference only under approved policy |
| SourceSpan | Document ID and normalized offsets; page range/bounding boxes for PDFs when available, paragraph/table location for DOCX; raw-to-normalized mapping, never invented page numbers |
| Clause | Stable document-scoped ID, visible label, parent, kind, original text and spans; duplicate labels may exist in separate scopes |
| Graph relation | Typed source/target IDs, raw expression, resolution method/status, alternatives, provenance and scope |
| Fact | Actor, modality, action, object, normalized value/unit, condition, effective interval, provenance and derivation version |
| Derived fact | Input-fact IDs, rule ID/version, effective state and unresolved assumptions |
| Finding | Category, deterministic candidate ID, severity basis, original/derived evidence, actual dependency paths, coverage and review states; confidence nullable unless calibrated |
| Source record | Source family, title/identity, URL, authority tier, jurisdiction, retrieved time, content hash, passage, issue/effective date and allowed-access metadata |
| Legal claim | Proposition, supporting passage IDs, identity/text-support/currency/applicability checks, limitations and professional-review triggers |
| Report | Version, owner, input hashes, as-of date, facts versus assumptions, findings/claims, pipeline/model versions, source metadata, coverage, cost/usage metadata and timestamps |

No numeric probability is added solely because the example report contains 94%.

## State separation

Job states: queued → running → succeeded, needs_review, failed or cancelled. Retries are attempts on one logical job, not duplicate reports. A report can be complete but still require professional review.

Document extraction: complete, partial, unsupported or failed, with affected-page coverage. Partial extraction cannot yield an apparently comprehensive report.

Reference resolution: resolved, ambiguous or unresolved, with explicit scope.

Model assessment: candidate, explained or uncertain. AI_REVIEWED means a model ran, not that a legal professional approved a conclusion.

Source checks: retrieved/failed; identity matched/unresolved; passage matched/unresolved; currency current-as-of/outdated/unknown; applicability supported/uncertain. If an aggregate VERIFIED label is retained for compatibility, its scope must be explained and all required checks must pass. It never certifies a judicial outcome.

## API compatibility decisions

Retain the existing /api/contracts/analyze multipart + 202/id contract during migration, and document the polling endpoint. Introduce source verification, rule diagnostics and document-linked research through explicitly versioned schemas. Do not invent a working /api/sources/verify route in documentation before it exists.

Contract, dispute and research share the report envelope, not one undifferentiated answer string. Unknown schema versions fail clearly rather than partially rendering.

## Data lifecycle invariants

- Ownership enforced at object, report, job and source-original fetch boundaries, not only in UI navigation.
- Save records explicit user intent; model retry or background completion cannot implicitly save.
- Delete/cancel/expiry cannot be reversed by a late worker, restore or retry. Tombstone strategy and backup suppression must be designed with the approved retention policy.
- Originals, extracted text, model payloads, queue inputs and backups each have explicit retention classification.
- Provider transmission requires an accurate disclosure/consent policy. store=False is not a complete provider-retention policy.
- Never include confidential text, passwords or API credentials in logs.
- No source scraping bypasses login, CAPTCHA or licence restrictions.

## Statistics

Count unique explicit references, resolved explicit references, term-use edges, definitions, active amendments and unresolved amendments separately. Count actionable candidates, explained candidates and uncertain assessments separately. Never fabricate target counts to match the pitch.
