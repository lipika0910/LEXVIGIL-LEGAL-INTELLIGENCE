# LexVigil implementation plan

## Managed private-account authentication checkpoint

Supabase credentials and server-confirmed identity checks are now connected behind `AUTH_PROVIDER=supabase`. Private ownership uses a Supabase-prefixed user identifier; legacy local accounts are preserved and are not merged by email. Both an opaque server-revocable session and an HTTP-only provider access cookie are required. Logout invalidates the app session even if the provider is unavailable. Email confirmation without a session stays on the sign-in page.

Development launch: `.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --env-file .env.supabase.development`. This file contains only the dedicated project's non-secret publishable configuration. The local preview was switched to this mode. Launch without that file for legacy local-mode regression tests (ensure no AUTH_PROVIDER override is inherited).

Verification: 82 backend tests passed; production bundle passed; all three local-mode Chrome workflows passed after restarting a stopped Vite server. The signed-out/confirmation UI test also passed in managed mode with a mocked signup response. Hosted public settings confirm email signup and mandatory email confirmation; a malformed token was rejected with provider status 403 (the adapter maps provider 401/403 to application 401). No hosted account was created or email sent.

Remaining Auth work: successful hosted account/email-confirmation test, approved redirect URLs and production SMTP, password recovery, session renewal and account deletion. Current managed sessions require re-login after at most one hour; no refresh tokens are retained. Report persistence remains in the existing API database, not Supabase tables. This checkpoint does not implement original-file storage, OCR, shared workspaces or production deployment.

Latest implementation checkpoint: [G1 typed ingestion and provenance](docs/implementation/G1-ingestion.md). This adds verified foundation work beyond the Phase 1 gap snapshot; it is not a production-readiness declaration.

## Active Phase 1 baseline — 2026-09-13

The current source-traceable release baseline is [docs/phase-1/README.md](docs/phase-1/README.md): 59 requirements with acceptance scenarios, dependencies, discrepancies and release gates. It is prepared, but not scope-approved or production-approved while remaining decisions are open.

Confirmed by the user during Phase 1: English plus Tamil and Hindi; temporary original-document storage with explicit consent, a 48-hour lifetime, automatic deletion and earlier manual deletion. Saving a report does not extend its original document's expiry. The 48-hour decision concerns originals, not the separate unsaved-report clock.

The earlier compact ledger below is historical context. Use the Phase 1 matrix for new implementation and acceptance tracking.

Reference: the definitive HTML package and project documentation supplied by the user. Embedded claims and demonstration figures are reference material, not verified product claims.

## Confirmed product choices
- Full platform: contract analysis, dispute analysis, legal research, and public introduction.
- Accounts with temporary processing by default and explicit opt-in saving.
- Preserve the supplied LV mark; adapt its presentation for the navy and blue interface.

## Delivery sequence
1. Establish React/TypeScript application, responsive navigation and evidence workbench.
2. Build FastAPI document ingestion, clause/reference/definition extraction and deterministic candidate reasoning with provenance.
3. Connect structured AI verification and retrieved-source research; expose unavailable providers honestly.
4. Add authentication, owner-scoped storage, export and deletion.
5. Test actual document changes, exceptions, clean inputs, access isolation and failure recovery; verify desktop/mobile behavior.

## Acceptance constraints
- Never return fixed sample findings for an uploaded document.
- Never treat a retrieved URL alone as proof of a legal proposition.
- Keep facts, inferred relationships and model interpretation distinct.
- Do not promise complete coverage, zero errors or calibrated confidence without measurement.
- Deployment requires working provider configuration and successful end-to-end validation.

## Requirement gap ledger (updated 2026-09-13)

| Requirement | Current implementation | Release condition |
|---|---|---|
| Public site and authenticated workspace | Implemented with supplied logo | Final product/content approval |
| PDF/DOCX/TXT/MD ingestion | Text PDFs and clause provenance; bounded file size | OCR, complex layouts, nested numbering and original-PDF viewer |
| Reference and term graph | Explicit numbered links, definitions, amendment links | Transitive effective states, general precedence and semantic edge evaluation |
| Twelve-category reasoning | Bounded local patterns; optional schema-constrained semantic assessment across taxonomy | Labelled benchmark across all categories; not a completeness guarantee |
| Three-tier model review | Configurable escalation for uncertain assessments; exact quote validation | Live provider access, quality/cost/latency evaluation |
| Dispute and research | Live official-domain retrieval adapter and source inspector | Verify actual provider run, statute versions, passage-level support, source coverage and legal reviewer signoff |
| Save/export/delete | Owner scoped; explicit save; JSON and complete printable contract report | Host backup and retention policy |
| Privacy | Temporary default, sign-out deletion, periodic sweep | Encryption at rest, consent/privacy policy and deployment-specific retention validation |
| Identity/security | Password hashing, opaque HTTP-only sessions, origin checks and local throttling | Email verification/recovery, distributed limits, security review and adversarial testing |
| Jobs and operations | Bounded single-process worker pool, visible restart failure | Durable queue, migrations, monitoring, backup/restore and load tests |
| Deployment | Local build and environment template | User chooses host/region; secrets, TLS, PostgreSQL and release smoke tests |

These remaining conditions are substantive work, not cosmetic checklist items. A passing local build must not be presented as full compliance with the definitive package or as production approval.
