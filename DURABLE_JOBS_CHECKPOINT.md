# Durable contract jobs — development checkpoint

Follow-up: upload execution now uses supervised child processes. See PROCESS_ISOLATION_CHECKPOINT.md for the newer implementation and verification; the thread-execution limitation below describes the earlier checkpoint.

Verified 2026-09-15. This is not a production-readiness declaration.

## Implemented

- Explicitly consented contract uploads reference the existing encrypted original from a SQLite queue. No second document copy or provider request is introduced.
- Two asynchronous worker loops use atomic claims, a 30-second lease and five-second heartbeats. Abandoned claims allow at most three attempts.
- Publication requires the current claim and an available original/report. Deleted or expired data cannot be resurrected by a late worker.
- Original and report deadlines are unchanged. Non-consented uploads and research remain memory-only and need resubmission after an API restart.
- Progress text distinguishes recoverable processing from memory-only processing. Original deletion warns about pending analysis.

## Verification

- Frontend TypeScript/Vite production build passed.
- Full backend diagnostic rerun: 112 passed, two dependency deprecation warnings, 11.15 seconds.
- Nine local browser regressions passed; managed-only test deliberately skipped in local mode.
- Supabase-enabled preview restored; managed login/recovery desktop/mobile smoke passed separately. No Google account credentials were submitted by automation.
- Child-process crash test uses a temporary synthetic database and a shortened one-second lease: abrupt exit, actual lease expiry, replacement claim, stale-result rejection and unchanged retention verified.
- An earlier final full-suite run stalled near the queue tests and was interrupted. The diagnostic rerun passed; the intermittent stall was not reproduced or attributed to a proven cause. Repeat/stress shutdown testing remains an open gate.

## Remaining deployment gates

- Durable production storage and PostgreSQL queue implementation; this queue is SQLite development only.
- Isolated processing workers with enforceable cancellation/resource limits; current processing uses threads and may continue computing after cancellation, though publication is fenced.
- Process-kill testing during extraction/OCR and across full API restart, plus repeated shutdown/concurrency stress tests. The child test kills a claimant before extraction, not a complete live API.
- Shared rate/quota controls before multiple API processes, hosted encryption-key recovery, backup/restore and deletion verification, monitoring and load testing.
- Hosting region/provider/budget and residency decisions remain necessary before provisioning production services.

Local preview: http://127.0.0.1:5173/login. After reboot run `npm run dev` from this project and keep its terminal running.
