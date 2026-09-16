# Vercel release assessment — 2026-09-16

Status: NOT APPROVED FOR PUBLIC DEPLOYMENT. A successful frontend build is not a functioning hosted backend.

## Confirmed user direction

- Vercel hosting; zero-cost operation requested.
- Business/law-practice use confirmed by the user. This is incompatible with Vercel Hobby's personal non-commercial restriction; paid Vercel approval or a different host is pending.
- Automatic fallback only to an eligible free AI model; no paid fallback authorized.
- India-focused residency requested; strict document/AI residency versus Indian-law market focus needs confirmation.
- A new GitHub repository with a main-branch v1 recovery checkpoint requested.
- Existing Supabase project mbnwdfdxksiuptwonjev remains development-only.

## Verified constraints

The current [Vercel Hobby documentation](https://vercel.com/docs/plans/hobby), checked on 2026-09-16, limits Hobby to personal, non-commercial use and functions to 300 seconds. The existing isolated OCR deadline is 660 seconds. The API also starts process-resident background workers, uses SQLite-only original/queue adapters, and creates tables on import. These are not a verified Vercel production architecture.

The configuration validator now refuses this API's startup when VERCEL=1 or VERCEL_ENV is preview/production. This is intentionally earlier than database initialization. Do not remove the guard merely to obtain a successful deployment. Replace it only alongside a tested hosted persistence/dispatch architecture and production security settings.

A selected India database region alone does not establish end-to-end India residency for AI, request routing, logs or backups. No free AI provider has yet been approved or verified for all required processing/residency conditions. Do not send documents to arbitrary free models.

## Required implementation order

1. Resolve hosting/cost for the confirmed business use and confirm exact residency scope.
2. Select an architecture that fits approved cost, region and duration constraints: durable external persistence, explicit job dispatch and bounded/restartable OCR work. If a separate worker is necessary, approve its host/cost first.
3. Implement PostgreSQL migrations, hosted encrypted-original storage, atomic shared quotas and multi-instance queue ownership; test cross-user isolation and retention/deletion on the actual hosted services.
4. Configure a separate production identity project, callback URLs, email delivery, secret recovery and least-privilege credentials. Never migrate the development project into production implicitly.
5. Implement a vetted provider allowlist and bounded free-only AI fallback. Record model provenance and unavailable states; never label unverified output as legally verified.
6. Validate Linux execution, real OCR language packs, startup/restart recovery, legal-quality benchmarks, backups/restores and deployed end-to-end workflows before release approval.

## This checkpoint's evidence

- Backend suite: 171 passed, 3 opt-in tests skipped, 2 dependency deprecation warnings; 30.93 seconds.
- Configuration tests: 32 passed, including hosted-preview/production refusal with missing, development, test and production settings.
- Frontend TypeScript/Vite production build passed.
- Local Git repository initialized with main as the branch. No commit, remote repository or push completed in this checkpoint.
- GitHub authenticated identity was readable; the available connector has no repository-creation operation. Browser creation fallback failed to initialize (Windows error 1058). Do not claim a remote recovery checkpoint exists.
- No production deployment, paid resource, provider request with document content, or production database migration performed.

Remaining product and legal acceptance gates are in docs/phase-1/release-gates.md. This assessment supplements, rather than replaces, those gates.
