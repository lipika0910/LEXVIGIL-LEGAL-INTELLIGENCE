# Deployment preparation — release blocked

This directory is not a ready-to-launch deployment. Do not route public traffic to the development server.

## Completed prerequisites

- Production startup rejects local-account authentication, non-HTTPS app origins, SQLite or unverified PostgreSQL TLS, the explicitly development-only Supabase project, missing/invalid encryption keys and unsupported API-worker counts. Errors do not echo secrets.
- `/api/health/live` answers whether the API is alive. `/api/health/ready` checks database access, installed OCR language packs, original storage and live durable-worker tasks. Both are unauthenticated, no-store probes without connection strings or document data. A ready response is operational status, not legal-quality or release approval.
- Production readiness currently returns 503 because the original/queue adapters are still SQLite-only. Do not remove this check simply to make a host deploy green.
- Database probes are single-flight and cached for five seconds. PostgreSQL connection and statement timeouts are bounded at five seconds.
- Environment files are excluded from Git except safe templates. Docker build context is deny-by-default; local databases, uploads, DPAPI keys and environment files are not included.
- `backend/requirements-runtime.lock` pins the installed Windows runtime versions. This is an input to future packaging, not a tested Linux/hash-locked artifact.

## Inputs required before provisioning

Latest verification on 2026-09-16: 158 standard backend tests passed (three opt-in API integration tests intentionally skipped in that run); all three opt-in drills passed in dedicated/full runs, including 32 stability cycles. Nine local browser workflows and the separate managed-login/recovery smoke passed. The frontend build passed. The managed development preview's live readiness check returned all four dependency checks healthy. Two dependency deprecation warnings remain. None of these results constitutes Linux/container, hosted PostgreSQL, legal-quality or production release acceptance.

1. Approved hosting provider, region/domain and monthly budget.
2. Whether originals and extracted legal text must remain in India for storage and processing.
3. Separate production Supabase project; never reuse `mbnwdfdxksiuptwonjev` as production.
4. Production secret storage and recovery ownership, SMTP/domain verification, backup retention and RPO/RTO.

No production resources, paid services, remote buckets or tables have been created here. Docker is not installed on the development machine; no container build/run has been validated. Do not describe the current preparation as a tested container deployment.

## Engineering and product release blockers

- Hosted original storage and PostgreSQL queue, versioned migrations, shared quota/rate controls and access-policy tests.
- Linux/container process limits and parent-death behavior; isolated PDF-preview rendering; remaining thread-based workflows.
- Built/pinned images, Linux dependency resolution/hashes/security scan, TLS/proxy trust, logs/metrics/alerts, backup restore and rollback drills.
- Full source/passage verification and legal-domain coverage, live provider integration/cost controls and multilingual explanation evaluation.
- Approved legal-review benchmarks and acceptance targets, privacy/account-deletion/backup policy, operational owner and staging/pilot approval.

The authoritative release gates remain `docs/phase-1/release-gates.md`. Passing tests or editing this checklist cannot waive them.

## Repeatable integration drills

PowerShell:

```powershell
$env:LEXVIGIL_API_DRILL='1'
.venv\Scripts\python.exe -m pytest backend/test_api_crash_drill.py -v -o faulthandler_timeout=90
```

The drills allocate their own loopback port, temporary database and random key. They use synthetic accounts/documents, observe real Tesseract execution, kill only their own API interpreter, and restart against the same temporary data. They cover consented recovery with the real 30-second lease, memory-only failure without persistence, and 32 repeated upload/OCR/download/preview/deletion cycles. They do not use the user preview or transmit data to AI providers.

Current Windows launcher correction follows CPython's own multiprocessing pattern: bypass the virtual-environment redirector with the base interpreter and `__PYVENV_LAUNCHER__`. This preserves the environment while ensuring the contained PID is the actual interpreter.

References: [CPython Windows multiprocessing launcher](https://github.com/python/cpython/blob/3.12/Lib/multiprocessing/popen_spawn_win32.py), [Microsoft process/job association](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject), [PostgreSQL TLS verification](https://www.postgresql.org/docs/current/libpq-ssl.html), [Supabase production checklist](https://supabase.com/docs/guides/deployment/going-into-prod).
