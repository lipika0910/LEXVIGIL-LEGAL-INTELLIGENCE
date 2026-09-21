# Existing LexVigil hosted database setup — 2026-09-19

Target: `mbnwdfdxksiuptwonjev`, Mumbai, selected explicitly for the personal
non-commercial demonstration. This checkpoint supersedes the empty-schema
state in DEMO_TARGET.md. Existing Supabase Auth accounts and OAuth settings
were not modified. The separate demo project remains untouched.

## Applied migrations

The existing, reviewed SQL migrations were applied through Supabase MCP.
MCP assigned new remote timestamps; the local source files retain the
timestamps of their original application to the separate demo project.
Do not blindly run CLI db push against this target until migration history
is reconciled; the matching names below are already applied.

| Local source version | Selected-project version | Name |
| --- | --- | --- |
| 20260917045635 | 20260919163918 | lexvigil_private_foundation |
| 20260917050133 | 20260919163927 | lexvigil_runtime_roles |
| 20260917094122 | 20260919163937 | lexvigil_admin_role_checks |

Five private tables now exist with enabled/forced RLS, restricted grants,
ownership constraints, original-retention checks and a retention-protection
trigger. Three NOLOGIN capability roles separate tenant, auth and worker
access. These are not yet password-authenticated application login roles.

## Verification

Both `supabase/tests/private_foundation.sql` and
`supabase/tests/runtime_roles.sql` passed on the selected project. Synthetic
writes were rolled back. Checks include account isolation, missing identity,
expiry filtering, prohibited field updates, auth/worker separation, browser
role denial, original-retention extension rejection and cascading deletion.
These SQL tests do not prove end-to-end automatic deletion scheduling,
real application login-role isolation, or authenticated encryption integrity.

Supabase security advisor reported one warning: leaked-password protection
is disabled. Official documentation states this feature requires Pro or
above. No paid upgrade or Auth setting change was made:
https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection

## Deployment status and next work

Vercel connector inspection still lists no LexVigil project in the selected
account. No deployment was created. Existing hosted-startup guards remain
enabled because the API still depends on local SQLite adapters and
process-resident jobs.

Next: securely provision three restricted login roles; test actual TLS
connections and transaction-context reuse; integrate PostgreSQL auth,
analysis, encrypted-original and leased-job adapters; implement shared
quotas and deletion scheduling. Then verify bounded OCR in the hosted
runtime and deployed end-to-end flows. Free India-only AI remains unresolved.

The Supabase skill guided least-privilege/RLS verification; the Vercel
deployment guidance requires verification before promoting a deployment.
No paid resource was enabled and no user document was sent to an AI provider.
