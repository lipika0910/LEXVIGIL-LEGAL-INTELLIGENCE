# Preview deployment — 2026-09-21

## Update — 2026-09-22

The user approved deletion of the unintended initial deployment. It was removed
successfully; the stable preview alias was verified separately and its health
endpoint still responds. The user then conditionally approved production runtime
credentials if recommended safe. Restricted server-only credentials were judged
appropriate for this personal demo and uploaded to this project's production
environment via stdin. No administrator credential was transferred. Preview and
production share the selected database; separate databases are recommended before
real law-practice use. The historical pending-deletion notes below are superseded.

A production candidate will be built without automatic domain assignment.
Real Google callback and authenticated hosted processing are still unverified.

- Project: `prj_R0tVgJx6m9mzO8Bbh19BErnAfoKv`, team `rakesh-projects`.
- Git branch: `codex/showcase-preview`; initial source commit `115d3c5`.
- Verified preview: `dpl_DjWWkeowM2DedMuBUPQ7TxNpti3H` (READY).
- Stable origin: https://lexvigil-git-codex-showcase-preview-rakesh-projects.vercel.app
- Deployment URL: https://lexvigil-171g2latd-rakesh-projects.vercel.app
- Function `api/index`: 59.96 MB, Mumbai `bom1`; Python 3.12.
- Build took place in US `iad1`. This is not an India-only hosting footprint;
  the configured application function runs in Mumbai and AI is disabled.

User explicitly approved restricted-password/publishable-key transfer to this
preview branch. Seven environment variables are branch-scoped; no database
administrator credential was transferred. Secrets never entered Git or CLI
arguments. The staged scan compared all 49 files against known secret values
before commit. CLI upload audit excluded local env files, runtime bundle,
databases, plans and test artifacts.

Hosted checks using authenticated Vercel curl:
- `/api/health`: correct showcase flags and 2 MB upload limit.
- `/api/auth/options`: managed authentication enabled.
- `/api/me`: 401 without a session.
- `/login`: 200 with the built SPA assets.
- `/api/auth/google/start`: successful PKCE initiation via the real restricted
  Supabase database connection and selected Supabase authorize endpoint.

No real Google callback or authenticated hosted document analysis has yet been
verified. User must test sign-in at the stable preview origin. If redirect is
rejected or falls back to localhost, update Supabase's allowed redirect URLs
for this origin without removing existing local URLs. Preview protection stays
enabled; user may need to authenticate with Vercel before app login.

## Unintended initial automatic build

Vercel marked the first GitHub-triggered build `dpl_AJFEaWCdChHu8HcqVBCWERJ5akMP`
as production, despite production branch `main`. It received no production
runtime credentials and is not a usable release. Its production aliases include
lexvigil.vercel.app. Explicit deletion approval has been requested; deletion was
blocked by approval review and has NOT occurred. The stable branch-preview
alias has been moved to the verified preview above. No main-branch merge or
promotion of the verified preview has occurred.

Remaining: remove the unintended build if approved, real callback/recovery and
authenticated upload/report checks, Linux child-process/timeout verification,
safe unexpected-error/readiness checks, then separately authorize production
credential scope and promotion. Do not call this a production-ready launch.
