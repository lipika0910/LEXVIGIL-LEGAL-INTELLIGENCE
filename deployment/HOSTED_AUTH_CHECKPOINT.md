# Hosted authentication persistence — 2026-09-20

Added an auth-only database facade for the existing PKCE and recovery routes.
`install_auth_flows(..., initialize_schema=False)` now supports migrations
instead of runtime CREATE TABLE. The existing local caller retains its
previous behavior; the running app has not switched to hosted persistence.

Fixed the hosted sessions constraint, which previously rejected the existing
`recovery:supabase:<UUID>` owner format. The replacement accepts only normal
or recovery-prefixed canonical UUID-shaped owners. Permissions and RLS are
unchanged. Local migration `20260920030450_lexvigil_recovery_session_owner.sql`
was applied as remote version `20260920030531` on `mbnwdfdxksiuptwonjev`.
As with earlier mappings, reconcile versions before CLI db push; do not replay.

Live database verification with `python -m scripts.check_hosted_auth` passed:
PKCE challenge verification, session persistence, replay denial, recovery
callback, single-use recovery and deletion of both session kinds after a
synthetic password update. This used a synthetic identity provider: no live
Google, real password change or recovery email was attempted. Test-owned
sessions and flows were removed. Actual user accounts were unchanged.

Security advisor still reports leaked-password protection disabled:
https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection

Next integration: wire hosted auth and report adapters into a bounded,
text-only showcase API; implement shared admission/cleanup; deploy and test
real callbacks and end-to-end report workflows. No Vercel deployment exists
as a result of this checkpoint, and hosted startup guards remain enabled.
