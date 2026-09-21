# Hosted runtime credentials and report persistence — 2026-09-20

Target: existing LexVigil `mbnwdfdxksiuptwonjev` in Mumbai.

## Completed

- Restricted login migration applied remotely as `20260919192058`.
  Local CLI-generated source is `20260919191945_lexvigil_restricted_logins.sql`.
  Do not replay it: reconcile migration versions before using CLI db push.
- Created `lexvigil_tenant_login`, `lexvigil_auth_login`, and
  `lexvigil_worker_login`. Each has exactly its matching capability membership
  with SET enabled, INHERIT and ADMIN disabled. Catalog checks confirmed no
  superuser, RLS bypass, role/database creation, or replication capability.
- Activated the initially passwordless NOLOGIN roles through verified TLS.
  Passwords were generated locally and persisted only as a Windows DPAPI
  encrypted bundle under ignored `.runtime/hosted-logins.dpapi`.
  PostgreSQL received SCRAM verifiers rather than plaintext password SQL.
  Existing administrator credentials and Supabase Auth accounts were unchanged.
- Live verification through the actual SQLAlchemy pools passed for all three
  logins, including capability validation and transaction-local role/identity
  reset across sequential reuse.
- New `HostedReports` repository passed a live synthetic two-account test:
  create/list/get/complete/save/delete; cross-account get/save/delete denial;
  wrong-owner publication rejection; duplicate publication rejection; and
  deleted-report resurrection rejection. Synthetic records were removed.
- Backend suite rerun after the interrupted session: 210 passed, 3 skipped,
  2 dependency deprecation warnings. This preceded the new provisioning and
  repository scripts; those received separate live checks described above.

## Reproducible checks

From the project root:

```powershell
.venv\Scripts\python.exe -m scripts.provision_hosted_logins
.venv\Scripts\python.exe -m scripts.check_hosted_reports
```

The first is read-only by default. Its explicit `--activate` mode never
resets an already-active login password. A missing/lost local bundle with
active remote logins requires an explicit credential recovery/rotation plan.
Never print/decode the bundle into chat, logs or tracked files. DPAPI binds
it to this Windows identity; it is not a portable deployment secret store.

## Remaining

The API still uses its existing local adapters. Wire hosted auth/session and
report repositories into the reduced showcase, add shared admission limits
and retention cleanup, and implement bounded text-only processing before
enabling Vercel startup. Then configure hosted secrets/OAuth callbacks and
verify deployed end-to-end flows. Connection tests do not prove login UI,
automatic cleanup, load resilience or full release readiness.

Security advisor still reports only leaked-password protection disabled.
No paid upgrade was made. Remediation and plan restriction:
https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection

No Vercel deployment, AI provider request, or new paid resource was created.
