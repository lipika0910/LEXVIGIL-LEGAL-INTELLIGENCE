# Integrated showcase API — 2026-09-20

Added `backend/showcase_api.py`: an injectable API factory using hosted auth
and report persistence, with no SQLite, startup DDL or process-resident queue.
It supports managed password sign-in/registration, existing PKCE/recovery
routes, identity lookup, text-contract/sample analysis, history, report
retrieval, save, delete and logout with unsaved-report deletion.

Processing uses the existing isolated rule-engine worker with a 20-second
deadline, OCR off and a 2 MB input limit. An ASGI body limiter also caps
chunked requests before multipart parsing. Origin checks protect mutations.
Database-backed minute-rate buckets use transaction advisory locks across
instances. Original storage, OCR and AI are absent from this API.

The integrated script `python -m scripts.check_showcase_api` passed using
real hosted restricted logins and the real isolated rule engine on Windows.
It checks synthetic sign-in, identity, wrong-origin denial, OCR rejection,
sample analysis, report retrieval, save, deletion and logout. Authentication
is a synthetic provider: this is not live Google or public deployment proof.
Test-owned reports/sessions are removed. Rate buckets expire after a minute.

## Still required before public deployment

- Deployment entry point, verified Linux/Vercel subprocess behavior and
  Mumbai function configuration; deliver restricted secrets securely.
- Hosted Linux process-containment validation. Independent compute leases and
  scheduled cleanup are implemented; see RETENTION_CHECKPOINT.md. Leased
  admission is not a platform-enforced global CPU cap under host suspension.
- Readiness probes, generic unexpected-error responses, request-duration
  review (frontend currently times out at 30 seconds), and dependency pinning.
- Showcase UI wording/2 MB upload limits, browser/accessibility tests,
  real Google callbacks, password recovery/email and deployment rollback.

## Follow-up validation — 2026-09-20

Hosted API admission now takes a cross-instance advisory lock before creating
the queued report: maximum 100 physical report rows, 10 per account, and four
queued/processing rows. Physical counts include expired records, failing
closed if cleanup is unavailable. Each completed payload remains capped at
2 MiB. This bounds report payload storage through this API, not total database
size, WAL, backups or other writers. Failed analyses remove their reservation.
Abandoned reservations still require cleanup/manual deletion.

The UI now rejects empty/oversized files before submission, advertises the
showcase 2 MB limit, and distinguishes rule-based contract review from deferred
AI/research/OCR. The development profile keeps its 15 MB upload limit.

Validation: 217 backend tests passed, three skipped, two dependency deprecation
warnings. TypeScript/Vite production build passed. Live restricted-role
Supabase integrated sample/save/delete/logout check passed with the real local
rule engine and a synthetic authentication provider. Five new admission unit
tests cover each limit, lock ordering and invalid identity rejection.

Browser invocation failed with Windows error 1058. User-approved Playwright
fallback passed four existing auth/recovery tests plus focused showcase
desktop/mobile checks. Account-changing responses were simulated. Complete
accessibility and real hosted Google callback acceptance remain pending.
Vercel inspection found no LexVigil deployment project.

Existing production guards remain unchanged. No Vercel deployment or paid
resource was created by this checkpoint. This factory is not automatically
selected by the existing local development launcher.
