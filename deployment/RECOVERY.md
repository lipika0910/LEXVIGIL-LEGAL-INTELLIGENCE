# v1 source recovery checkpoint

This checkpoint preserves source code, tests, safe configuration templates, supplied reference plans and brand assets. It is **not a production release**, a database backup, or evidence that all planned features work in a hosted environment.

## What is deliberately excluded

- Local databases and uploaded documents, including extracted reports and accounts.
- Environment files, API credentials, DPAPI encryption keys and Vercel local configuration.
- Installed dependencies, generated build output, OCR runtime/language packs and browser artifacts.

Recover these only through an independently approved encrypted backup/secret-recovery process. A source checkout cannot decrypt an old original without its correct key. Never generate a replacement key over an existing encrypted data store. See ENCRYPTION_RECOVERY.md.

## Restore source on the current supported development platform

1. Clone the private repository after remote publication is verified. Check out the `v1` tag for this checkpoint, or `main` for subsequent changes. Until publication is verified, only the local repository exists.
2. Install Node.js and Python 3.12. Create a new `.venv` and run `npm ci`.
3. Install `backend/requirements-runtime.lock` inside the virtual environment. It pins the tested Windows runtime; Linux dependency validation remains pending. Install pytest separately for test execution.
4. Follow OCR_SETUP.md for Tesseract and the English, Tamil and Hindi language files. Do not assume they were committed with source.
5. Create `.env.supabase.development` from safe template information and your own development project configuration. Never use production credentials for local synthetic tests.
6. Run backend tests and `npm run build`. Use `npm run dev` for managed development authentication, or `npm run dev:local` for isolated synthetic-account browser tests.
7. Verify login, account isolation, upload, OCR, evidence, expiry and deletion before trusting the restored instance. Reconfigure allowed identity-provider callback URLs if the origin changes.

## Publication and deployment are separate

A GitHub push provides a remote source checkpoint, not deployment or data recovery. Verify the remote `main` commit and `v1` tag both match the intended local revision. Never force-push to an existing unrelated repository.

Public deployment remains blocked by deployment/VERCEL_READINESS.md and docs/phase-1/release-gates.md. Business use was confirmed; no paid hosting approval or alternative hosting selection has been received. No paid service or overseas document processing is implied by this checkpoint.
