# LexVigil hosted demo foundation

Approved project: `rhtbctgvqpvmiqmnegwh` (LexVigil Demo), Rakesh-IN Org, Mumbai `ap-south-1`. Creation quote was 0 monthly. Development project `mbnwdfdxksiuptwonjev` is not a migration target.

## Applied and verified on 2026-09-17

Migration `20260917045635_lexvigil_private_foundation.sql` creates five tables in `lexvigil_private`. It grants no application/browser access. RLS is enabled and forced, with no permissive policies. No public tables, storage buckets, OAuth configuration, credentials or documents were created/copied by this migration.

The filename was generated with Supabase CLI 2.117.0, then synchronized to the actual version recorded by the remote MCP migration operation. Do not apply a second copy under the original local generation timestamp.

The repeatable SQL check in `tests/private_foundation.sql` passed on the hosted demo database. Synthetic writes run within a rolled-back transaction. Checks cover RLS flags, cross-owner foreign-key denial, retention over 48 hours, retention-extension/consent-clock denial, saving without extending retention, cascade deletion, and denied SELECT for anon/authenticated roles. Post-test analyses, originals and jobs counts were zero.

The encrypted payload constraints validate envelope shape and size only. They do not establish cryptographic authenticity: the application must still perform AES-GCM verification. The synthetic SQL test deliberately uses format-only bytes and does not represent an encrypted customer document.

Security advisor: zero warning/error findings in this check; five informational RLS-without-policy findings, expected for the closed foundation. [Advisor explanation](https://supabase.com/docs/guides/database/database-linter?lint=0008_rls_enabled_no_policy).

## Still required before connecting the app

- Least-privilege runtime/worker roles, reviewed authorization policies, and pooled transaction-local identity handling. Never connect the application as the migration administrator or grant browser roles broad access.
- PostgreSQL adapters and removal of production startup DDL; atomic quota/lease handling across instances; expiry access checks and scheduled deletion. Constraints alone do not execute automatic deletion.
- Review BYTEA capacity against the free database allowance or implement a private object-store adapter. Current development quotas must not be copied without hosted capacity validation.
- Secret provisioning and encryption-key recovery; authenticated original viewing; hosted isolation and concurrency tests.
- Bounded OCR jobs compatible with host limits; no foreign-region failover. No Vercel deployment has been made.
- Fully free India-only AI routing remains unimplemented. Starter-credit-only providers are excluded by the user's latest answer. Legacy AI calls remain disabled.

This is a tested schema foundation, not evidence of a working hosted application or completed production release.
