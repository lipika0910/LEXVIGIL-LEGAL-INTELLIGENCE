# Hosted capability roles — 2026-09-17

Applied to LexVigil Demo only (`rhtbctgvqpvmiqmnegwh`, Mumbai). The runtime-role migration is `20260917050133`; administrator role-assumption migration is `20260917094122`. Local CLI-generated filenames were synchronized with remote migration history.

- `lexvigil_tenant`: owner-scoped live analysis/original/job access; queued record creation; save/delete operations. Cannot publish analysis results, reassign ownership, inspect session records, or truncate tables.
- `lexvigil_auth`: session and PKCE-flow storage only; no contract access.
- `lexvigil_worker`: cross-account processing/cleanup access to analyses, originals and jobs; no authentication-flow access and no right to change a user's save choice or original retention.

All three roles are NOLOGIN, non-superuser, NOBYPASSRLS and cannot create roles/databases. No runtime passwords or application login memberships were provisioned. Browser roles remain excluded. The existing `postgres` administrator may explicitly SET ROLE for testing/maintenance, without automatic inheritance or delegated role administration. Never use that administrator as the application's database login.

## Verified

`tests/runtime_roles.sql` passed against the hosted database after the explicit administrative SET ROLE permission was added. It verifies missing identity denial, two-account analysis isolation, expired-unsaved filtering, saved-report visibility, cross-owner write denial, result/owner column protection, denied session access and truncation, worker/auth separation, role flags and transaction-local identity reset after rollback. All synthetic writes were rolled back. Security advisor returned no findings before the administrative membership migration; recheck after future access changes.

This is not proof of all original/job policies, concurrent connection-pool behavior or integrated API authentication. The tests exercise PostgreSQL roles and synthetic identities directly, not real user sign-ins.

## Required integration contract

The trusted backend must verify identity with Supabase before setting `lexvigil.owner`. Use `set_config('lexvigil.owner', verified_owner, true)` within every transaction; never accept this value from client input or retain it at connection/session scope. A role holding a database connection can set this context, so these policies are defense against omitted filters, not a substitute for backend authentication or SQL-injection prevention.

Keep separate least-privilege login credentials/pools for tenant, auth and worker capabilities. Add PostgreSQL adapters, atomic quota/lease operations, privileged-role rejection, pooling/restart tests, deletion scheduling and hosted end-to-end checks before connecting or deploying the application. Current local SQLite flows are unchanged.
