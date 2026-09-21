# Hosted entry point — 2026-09-21

`api/index.py` constructs the showcase factory through
`backend/showcase_bootstrap.py`. It does not import legacy `backend.app`, load
dotenv files, create SQLite databases, run startup DDL, or start a background
worker. Local development continues to use the existing launcher.

## Required server-side environment

- `LEXVIGIL_RELEASE_PROFILE=showcase`
- `SUPABASE_URL=https://mbnwdfdxksiuptwonjev.supabase.co`
- `SUPABASE_PUBLISHABLE_KEY`: existing project's publishable key, not service role.
- `APP_ORIGIN`: exact approved HTTPS deployment origin, no trailing slash/path.
- `LEXVIGIL_DB_TENANT_PASSWORD`, `LEXVIGIL_DB_AUTH_PASSWORD`,
  `LEXVIGIL_DB_WORKER_PASSWORD`: three separate restricted-login credentials.

Never prefix credentials with VITE_ or put them in frontend assets. Supply only
to the specifically approved Vercel environment; untrusted branch previews must
not inherit these database credentials. The local DPAPI bundle is excluded from
deployment and must never be uploaded as a file. No secret transfer was performed
in this milestone.

When `VERCEL=1`, bootstrap requires platform `VERCEL_REGION=bom1`; missing/wrong
region fails closed. `vercel.json` requests Mumbai with no failover region. The
public CA certificate is included for pooler verify-full TLS. HTTPS origin,
selected Supabase project, publishable key and distinct passwords are validated
before any connection factory is called.

## Build and routing candidate

Vite builds using npm ci / npm run build, with dist as static output. API routes
rewrite to the Python entry; other routes fall back to the SPA. Python function
duration is configured to 60 seconds; the document child has its own 20-second
deadline. Direct Python dependencies are pinned to installed/tested versions in
root requirements.txt. Transitive resolution and Linux wheels are not yet locked
or verified in a hosted build.

.vercelignore excludes local secrets, runtime state, SQLite databases, plans,
tests and development-only files. Function packaging explicitly includes backend
modules and the public certificate. Actual upload manifest/bundle contents,
rewrite path preservation, Vercel schema acceptance, region reporting and Linux
subprocess containment must still be inspected during preview deployment.

## Verification

Fifteen focused unit tests passed: unsafe origin/project/key/profile/region and
missing/shared runtime passwords rejected before constructing connections;
correct construction and pool disposal on setup failure verified.

Read-only `python -m scripts.check_showcase_bootstrap` passed with real restricted
credentials: all three database capabilities connected, managed auth options
rendered in API responses, anonymous workspace access returned 401. This was a
local Windows TestClient check, not a hosted Google authentication test.

## Remaining release gates

No Vercel project, deployment URL, hosted secrets or paid resource was created.
Before promotion: verify deployment routing/Linux behavior, choose the stable
origin and authorize its Supabase/Google callback, exercise real sign-in/recovery,
file upload/save/delete/export, test safe unexpected-error handling and readiness,
review frontend timeout against hosted latency, and record rollback evidence.
Build success alone is not deployment acceptance. AI/OCR/original storage stay
disabled; no India-only AI processing claim is made for a service not enabled.
