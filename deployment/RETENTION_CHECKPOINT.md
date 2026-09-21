# Hosted retention and compute admission — 2026-09-21

Target: existing Mumbai project `mbnwdfdxksiuptwonjev` only.
Local cleanup migration `20260920070454` maps to remote `20260920070622`.
Do not blindly push the differently timestamped local migration history.

## Active database maintenance

`lexvigil-private-retention-v1` runs every minute. A successful scheduled run
was rechecked on September 21 at 16:29 UTC. It deletes expired unsaved reports,
originals, application sessions and auth flows in batches of up to 1,000 each.
Saved reports and active sessions are preserved. Supabase Auth accounts and
provider settings are untouched. Original storage remains disabled in the demo.

Queued/processing reports older than 120 seconds without a durable contract-job
record are marked failed, allowing users to delete and retry them. Other durable
jobs are excluded. Only this maintenance job's logs older than seven days are
pruned. Worker/auth operations use separate restricted roles, SECURITY INVOKER
functions, an empty search path, statement/lock timeouts and a transaction.
Browser/tenant roles cannot execute these functions.

Rollback-only hosted SQL tests passed for expired removal, saved/active
preservation, abandoned recovery and fresh-request preservation. See
`supabase/tests/showcase_cleanup.sql`. Original expiry is implemented but was
not independently fixture-tested in that SQL check.

## Independent processing leases

The showcase API now holds a separate token in the private auth-flow store,
under a dedicated purpose and transaction advisory lock. At most four unexpired
leases can be acquired. Report deletion/logout cannot delete these tokens.
No document content or account identity is stored in a compute lease.

The lease is released after the supervised processor returns/unwinds, including
cancellation. A failed release is logged without private database details;
hard-crash leases expire after 120 seconds and are removed by cleanup/acquisition.
The real processor has a separate 20-second execution deadline. Acquisition
delayed more than 30 seconds is refused before starting processing.

This is a cooperative leased limit, not a platform-enforced global CPU cap:
server suspension or an orphan surviving its lease requires hosted Linux
process-containment validation. Do not claim a hard compute ceiling until that
behavior is verified on the deployment platform.

## Operational boundaries

RLS denies expired temporary reports immediately; physical deletion follows a
successful job run. Paused/unavailable free projects and backlogs can delay
deletion. SQL deletion does not erase backups or downloaded copies. Failed
reports still count toward storage quotas until deletion/expiry.

To suspend maintenance, deactivate only the named job in Supabase Cron. Do not
drop pg_cron, which removes all jobs. Review job_run_details for failures;
automated failure notification is not configured.

No Vercel release or paid resource was created by this work. The hosted showcase
factory is still separate from the legacy local launcher. Deployment bootstrap,
secure environment delivery, Linux execution and real hosted auth remain gates.
