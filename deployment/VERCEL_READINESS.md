# Vercel release assessment — 2026-09-16

Status: NOT APPROVED FOR PUBLIC DEPLOYMENT. A successful frontend build is not a functioning hosted backend.

## Superseding clarification — 2026-09-17

The user confirmed the first hosted release is a personal, non-commercial demonstration and that AI processing must remain entirely in India. This supersedes the earlier business-use answer below. Zero cost remains required. GitHub publication is now verified: main and the annotated v1 tag in Rakesh-IND/LexVigil both resolve to 7d202143897b663165e9e71ed17793c8419c3fd7. That tag is a source recovery baseline, not a deployed release.

Legacy live OpenAI calls are blocked at API admission and provider construction; merely adding a key cannot enable them. Local parsing and OCR remain available. Free, India-only model routing is still an open implementation requirement, not satisfied by disabling AI.

Provider research: Sarvam documents India-hosted inference and starter credits followed by per-use charges. Starter credits may support a finite zero-spend demonstration, but do not establish an ongoing free service. Account credit availability, hard no-payment behavior, eligible models and request/log retention need verification before integration. Sources: https://www.sarvam.ai/epoch/summary and https://www.sarvam.ai/api-pricing (checked 2026-09-17). No provider account was created and no document was transmitted.

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
