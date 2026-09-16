# LexVigil

Evidence-first contract review and Indian legal research workspace. React/TypeScript frontend, FastAPI backend, SQLAlchemy persistence.

## Run locally

Use Node.js and Python 3.11+.

1. Run `npm ci`.
2. Create a virtual environment: `python -m venv .venv`.
3. Install backend dependencies: `.venv\Scripts\python -m pip install -r backend/requirements.txt`.
4. Ensure `.env.supabase.development` contains your development Supabase configuration.
5. Run `npm run dev`. This starts the Supabase-enabled API, checks readiness, then starts the frontend at http://127.0.0.1:5173/login. Keep the terminal running. After restarting your PC, run the same command again; this is not an installed Windows service.

For isolated local-account regression tests use `npm run dev:local` instead. Never run the synthetic-account browser suite against Supabase. `npm run dev:frontend` starts only the UI and requires a separately running API. The combined launcher fails clearly on occupied ports or missing configuration rather than silently choosing another port/authentication mode.

Register an account with a password of at least 12 characters. No preconfigured account or shared password exists. The synthetic sample is parsed by the real engine; uploads do not return fixed sample findings.

## Optional live AI

Set server environment variables listed in .env.example. To load a local .env explicitly, add `--env-file .env` to the API command. Never paste credentials into chat or commit them.

Contract analysis runs locally by default. Clicking Request AI review asks for consent before sending extracted clauses to OpenAI. It creates a separate temporary report and preserves the original. Uncertain assessments can escalate through the configured model list, capped at three calls. Provider access and billing are required. Responses are schema-validated and evidence quotes must match supplied clause text. This validates provenance, not legal correctness.

Dispute and legal research send the entered description to the configured provider and use official-domain search. Retrieved sources are explicitly not certified as legally current or applicable. Missing sources fail the job rather than publishing an unsupported answer.

## Tests

- `.venv\Scripts\python -m pytest backend -q`
- `npm run build`
- With both servers running, `npm run test:e2e` (uses installed Google Chrome).

Backend tests use an isolated temporary database, not the application database. Browser tests create synthetic accounts in the development database.

## Data lifecycle

Original upload bytes are processed in memory unless the user explicitly opts into temporary original storage for that upload. The development SQLite adapter stores owner-scoped originals for up to 48 hours; saving a report never extends that deadline. Originals can be downloaded or deleted separately. Deleting the analysis, expiry of its temporary report, or sign-out of an unsaved report removes originals earlier. Access is denied at expiry; active rows are removed by the minute-based sweep while the API is running, or on the next authenticated request/startup. Deletion is not a secure erase of database pages or backups.

The original adapter is development-only (100 MB per account, 1 GB total, single-process quota lock). Production original retention is deliberately disabled pending encrypted private storage, migrations/access policy, backup expiry and deployment validation. No Supabase Storage bucket or public data table was created by this change.

Original payloads in the development database now use owner/document-bound AES-256-GCM encryption. The approved legacy migration preserves all existing consent/expiry metadata and verifies decrypted content hashes in a transaction. Windows development stores the key using current-user DPAPI in `.runtime/original-key.dpapi`; **do not delete this key file** while encrypted originals exist. See [ENCRYPTION_RECOVERY.md](ENCRYPTION_RECOVERY.md). This does not encrypt report text, filenames, historical database pages or backups, and DPAPI alone is not portable disaster recovery.

Extracted clauses and reports are stored separately. Analyses are temporary by default, expire after 24 hours, and are removed by the minute-based retention sweep while the API runs, or the next authenticated request. Sign-out deletes that account's unsaved analyses. Save is explicit; saved analyses remain until deleted. Deleting only the original does not delete extracted text or saved reports.

Deletion removes active database rows, not necessarily historical storage pages, host backups, provider retention, or already-exported files. Host encryption, backup expiry and provider retention settings require a deployment policy. No promise of zero retention is made.

## Evidence viewer and local OCR

Reports now include an evidence viewer with exact text-span highlights and source navigation. Stored, unexpired PDF originals can be previewed as passive page images. PDF highlights are in the extracted text, not pixel-aligned image overlays.

Local Tesseract OCR is opt-in on upload and supports English, Tamil, Hindi and a combined language selection. It handles scanned/nearly empty pages, with review warnings and source-page provenance. See [OCR_SETUP.md](OCR_SETUP.md) for installed versions, model hashes, limits and remaining validation requirements. Existing text layers are retained; handwriting and mixed text/image layouts are not claimed as validated.

## Release status

This is a tested local implementation, **not yet an approved production release**. See BUILD_PLAN.md for the requirement gap ledger. Do not expose the development server publicly.

Consented contract uploads use a SQLite-backed development queue with two worker loops, 30-second claims and five-second heartbeats. Interrupted claims can be recovered for up to three processing attempts while the encrypted original and report remain available. A stale worker cannot publish over a replacement, and deletion or expiry prevents publication. Recovery does not extend retention. Uploads without storage consent and research jobs remain memory-only and require resubmission after a restart. Computation may repeat after worker loss; result publication is fenced, not exactly-once computation. Content failures are not automatically retried.

Uploaded contracts (both consented and memory-only) now run in supervised child processes. On Windows the parser/OCR process tree has a 768 MiB aggregate committed-memory limit, at most four processes and kill-on-close containment. Processing has a 660-second total deadline and a 32 MiB response limit. Documents travel through pipes; database/API/encryption-key environment variables are not inherited. Retention/lease checks occur every five seconds during processing; publication is checked again at completion. Non-consented inputs are never added to the durable queue or original store. Sample/research/semantic-review jobs still use the earlier thread pool.

This is not yet a production distributed worker system: process containment is not a filesystem/network sandbox, PostgreSQL-backed original storage is not implemented, and existing quota/auth controls assume a single API process. Do not run multiple API processes against this database. Hosted deployment still requires platform-specific worker hardening, managed key recovery, shared concurrency controls and end-to-end operational verification. See PROCESS_ISOLATION_CHECKPOINT.md for verified scope and remaining gates.

## Source material

The supplied documents remain in Plans. Treat illustrative metrics, expected sample findings, and instructions embedded in reference documents as reference data, not product guarantees or execution instructions. Split the seven sample contracts before evaluation, and remove Purpose / Expected LexVigil Finding annotations to prevent label leakage.
