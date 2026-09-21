# Current phase — 2026-09-19

## Latest checkpoint — 2026-09-21

Restricted hosted logins and showcase report/auth adapters have passed live
synthetic integration checks. Approved Playwright fallback passed four existing
browser tests plus focused showcase desktop/mobile checks. Scheduled retention
is active with successful executions confirmed. Independent processing leases
now survive report deletion and pass live restricted-role admission checks.
See `RETENTION_CHECKPOINT.md` for details and remaining limitations.

Phase 4 remains active. Next: deployment bootstrap and secret delivery, Mumbai
Linux-runtime/process-containment verification, then real hosted auth and
end-to-end acceptance. No Vercel release exists yet. OCR/original storage/live
AI remain deferred for the showcase. The connection-only next step below is
historical and has been completed.

Active work: **Phase 4 / G4 — Production engineering**, using the numbering
in `docs/phase-1/release-gates.md`. G0 is the requirements baseline, not a
separate implementation phase among 1–7.

| Phase | Package | Current interpretation |
| --- | --- | --- |
| 1 / G1 | Typed ingestion | Local implementation and fixture evidence exist; release acceptance remains separate. |
| 2 / G2 | Reasoning core | Implementation exists; complete category coverage and legal-quality acceptance are not declared here. |
| 3 / G3 | Research and AI | Incomplete: live free India-only AI and live source/quality verification remain open. |
| 4 / G4 | Production engineering | Active: database integration, credentials, durable jobs, shared limits, encryption and retention. |
| 5 / G5 | Staging | Preparation only; no LexVigil Vercel deployment yet. |
| 6 / G6 | Release acceptance | Pending complete staging, benchmark, security, fault and user-flow evidence. |
| 7 / G7 | Pilot and launch | Pending acceptance, controlled pilot and release approval. |

These phases overlap. Working on Phase 4 does not mean Phases 1–3 are fully
accepted, nor does it imply a numerical completion percentage. Some baseline
acceptance thresholds and reviewer decisions also remain open.

## Connection implementation checkpoint

`backend/hosted_connections.py` constructs separate SQLAlchemy pools for
fixed tenant/auth/worker login names on the explicitly selected Mumbai
session pooler. Configuration validation requires distinct long passwords,
a loadable trusted CA, verified TLS, bounded pool sizes/timeouts and masked
SQL parameters. Partial construction failure disposes already-created pools.
The existing transaction helper additionally checks actual database role
capabilities on every transaction.

33 focused unit tests passed across the connection factory and transaction
helper. These tests do not provision logins or establish successful live
restricted-role authentication. No app.py integration or hosted-startup
guard removal was performed. The one-connection limit is per capability
per process, not a global cap across serverless instances.

Next: provision restricted logins through a secret-safe workflow, validate
live transactions and pool reuse, then integrate the hosted adapters.
