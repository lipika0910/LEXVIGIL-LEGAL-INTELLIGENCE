# Process isolation — development checkpoint

Implementation date: 2026-09-15; verification continued on 2026-09-16.
This is not a production-readiness declaration.

## Implemented scope

- Uploaded contracts, both consented and memory-only, run in a separate Python process. The child imports the contract engine, not the API, authentication or database modules.
- Input and output use pipes, not intermediate document files. The child environment allowlist excludes database URLs, Supabase/OpenAI credentials and the original encryption key. This is credential-inheritance reduction, not protection against a compromised process reading the same user's filesystem.
- Windows Job Objects contain the parser and OCR descendants with kill-on-close, a 768 MiB aggregate committed-memory limit, and at most four processes per job. Containment must attach before input is sent; attachment failure aborts processing. Parent death closes the job handle and terminates its process tree.
- Total execution deadline: 660 seconds; output cap: 32 MiB. Existing upload/page/OCR limits remain. The supervisor kills the process tree on timeout, cancellation or failed retention/lease renewal. Windows descendant termination is asynchronous; tests use bounded polling to verify exit.
- Durable work checks its current lease and original/report retention every five seconds, and checks publication again on completion. Retention loss cannot restore deleted data or publish a late result. No retention deadline is extended.
- Non-consented uploads have two lifecycle-scoped slots, no original-store entry, and no durable-queue entry. Shutdown stops active children and marks pending memory-only work failed; abrupt restart still requires resubmission. Durable and memory-only processing each have two slots in this single API process.
- The old nested heartbeat cleanup pattern, which could consume cancellation during shutdown, was removed. Repeated completion/shutdown cycles are tested. This does not prove it was the cause of the previously observed intermittent stall.
- The launcher now identifies which service exited and records its PID, exit code and signal without printing credentials or OAuth URLs.

## Verification evidence

- Complete backend suite: 134 passing tests, two dependency deprecation warnings.
- Focused process/queue/memory lifecycle suite: 31 tests. Covers actual parser and descendant termination, supervisor crash, bounded response, Windows memory limit, containment failure, credential environment exclusion, malformed responses, lease loss, deletion/expiry and repeated shutdown.
- Real Tesseract OCR inside containment returns a provenance-labelled English report. Existing English/Tamil/Hindi OCR tests also remain in the complete suite; isolated multilingual OCR accuracy needs broader fixtures.
- Frontend TypeScript/Vite build passed.
- Local Playwright rerun: nine passed, managed-only test intentionally skipped. Includes real upload, OCR, evidence preview, source highlighting, saving/export, owner-facing deletion and auth flows.
- OCR browser checks assert page identity, meaningful login/report content, no Vite overlay, no unexpected console/page errors, and real source/image output. Desktop and 390 x 844 mobile screenshots are outside the repository under the configured Codex visualization directory.

## Open incident and remaining gates

An earlier browser suite lost the local API, after which the combined launcher stopped the frontend. Five tests had passed; four failed, including connection-refused errors. The previous launcher did not record the originating service/exit code. No matching Python/Node Application Error event was found in the inspected Windows event log. A clean, standalone browser rerun passed all nine tests. Root cause is unresolved; do not call this incident fixed merely because the rerun passed. New exit diagnostics are in place for recurrence.

Remaining production work includes:

1. Full Windows API-process crash/recovery during active Tesseract now passes for both consented and memory-only uploads, using the real 30-second lease and an isolated temporary database. The API also survived 32 paired/sequential upload, OCR, download, preview and deletion cycles. This is a bounded development stability check, not production load/soak certification. Longer staging tests and monitoring for the unresolved preview exit remain required.
2. Production worker OS/container isolation, restricted filesystem/network access, shared quotas and rate limits. POSIX process-group/resource-limit code has not been verified on a deployment host and does not provide the same verified Windows parent-death guarantee.
3. Sample/research/semantic-review jobs still use the prior thread pool; PDF-page preview rendering still runs in the API. These are outside this upload-processing isolation milestone.
4. Hosted PostgreSQL queue/original storage, managed encryption-key recovery, backup/restore and deletion verification, region/residency/budget decisions, and deployment automation.

## Design references

Follow-up on 2026-09-16: the Windows venv launcher was observed to have a different PID from its real interpreter. Processing now uses CPython's own base-interpreter launch pattern while preserving the venv, so containment attaches to the actual interpreter before document bytes are sent. A PID/environment regression test was added. See deployment/README.md for production configuration/readiness checks and outstanding release blockers.

- [Python 3.12 subprocess management](https://docs.python.org/3.12/library/subprocess.html): pipe transport and explicit child environment.
- [Microsoft Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects): process-tree containment and kill-on-close behavior.
- [Microsoft extended job limits](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information): memory and active-process limits.

Preview address: http://127.0.0.1:5173/login. Start both managed-auth services with `npm run dev`; this is not an installed Windows service.
