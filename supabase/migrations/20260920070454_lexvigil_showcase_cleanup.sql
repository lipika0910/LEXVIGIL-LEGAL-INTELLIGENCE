-- Restricted, bounded retention maintenance. No security-definer functions.
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE INDEX auth_flows_purpose_idx ON lexvigil_private.auth_flows(purpose);
CREATE INDEX analyses_abandoned_idx ON lexvigil_private.analyses(created)
 WHERE status IN ('queued','processing');

CREATE FUNCTION lexvigil_private.cleanup_reports() RETURNS jsonb
LANGUAGE plpgsql SECURITY INVOKER SET search_path = '' AS $$
DECLARE originals_removed integer; reports_removed integer; interrupted integer;
BEGIN
 DELETE FROM lexvigil_private.originals WHERE analysis_id IN (
  SELECT analysis_id FROM lexvigil_private.originals
  WHERE expires<=extract(epoch FROM statement_timestamp())
  ORDER BY expires LIMIT 1000);
 GET DIAGNOSTICS originals_removed = ROW_COUNT;
 DELETE FROM lexvigil_private.analyses WHERE id IN (
  SELECT id FROM lexvigil_private.analyses
  WHERE saved=0 AND expires<=extract(epoch FROM statement_timestamp())
  ORDER BY expires LIMIT 1000);
 GET DIAGNOSTICS reports_removed = ROW_COUNT;
 UPDATE lexvigil_private.analyses SET status='failed',
  error='Processing was interrupted. Delete this report and retry.',result=NULL
 WHERE id IN (
  SELECT a.id FROM lexvigil_private.analyses a
  WHERE a.status IN ('queued','processing')
  AND a.created < extract(epoch FROM statement_timestamp())-120
  AND NOT EXISTS (SELECT 1 FROM lexvigil_private.contract_jobs j WHERE j.id=a.id)
  ORDER BY a.created LIMIT 1000)
 AND status IN ('queued','processing');
 GET DIAGNOSTICS interrupted = ROW_COUNT;
 RETURN jsonb_build_object('originals_removed',originals_removed,
  'reports_removed',reports_removed,'interrupted',interrupted);
END;
$$;
CREATE FUNCTION lexvigil_private.cleanup_auth_records() RETURNS jsonb
LANGUAGE plpgsql SECURITY INVOKER SET search_path = '' AS $$
DECLARE sessions_removed integer; flows_removed integer;
BEGIN
 DELETE FROM lexvigil_private.sessions WHERE token IN (
  SELECT token FROM lexvigil_private.sessions
  WHERE expires<=extract(epoch FROM statement_timestamp())
  ORDER BY expires LIMIT 1000);
 GET DIAGNOSTICS sessions_removed = ROW_COUNT;
 DELETE FROM lexvigil_private.auth_flows WHERE token IN (
  SELECT token FROM lexvigil_private.auth_flows
  WHERE expires<=extract(epoch FROM statement_timestamp())
  ORDER BY expires LIMIT 1000);
 GET DIAGNOSTICS flows_removed = ROW_COUNT;
 RETURN jsonb_build_object('sessions_removed',sessions_removed,'flows_removed',flows_removed);
END;
$$;
REVOKE ALL ON FUNCTION lexvigil_private.cleanup_reports() FROM PUBLIC,anon,authenticated,service_role;
REVOKE ALL ON FUNCTION lexvigil_private.cleanup_auth_records() FROM PUBLIC,anon,authenticated,service_role;
GRANT EXECUTE ON FUNCTION lexvigil_private.cleanup_reports() TO lexvigil_worker;
GRANT EXECUTE ON FUNCTION lexvigil_private.cleanup_auth_records() TO lexvigil_auth;

SELECT cron.schedule('lexvigil-private-retention-v1','* * * * *',$job$
 BEGIN;
 SET LOCAL statement_timeout='10s';
 SET LOCAL lock_timeout='2s';
 SET LOCAL ROLE lexvigil_worker;
 SELECT lexvigil_private.cleanup_reports();
 RESET ROLE;
 SET LOCAL ROLE lexvigil_auth;
 SELECT lexvigil_private.cleanup_auth_records();
 RESET ROLE;
 DELETE FROM cron.job_run_details WHERE runid IN (
  SELECT d.runid FROM cron.job_run_details d JOIN cron.job j USING(jobid)
  WHERE j.jobname='lexvigil-private-retention-v1'
  AND d.end_time < now()-interval '7 days'
  ORDER BY d.end_time LIMIT 1000);
 COMMIT;
$job$);
