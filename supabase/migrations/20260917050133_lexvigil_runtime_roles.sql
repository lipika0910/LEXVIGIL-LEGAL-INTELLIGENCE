-- Non-login capability roles. Provision separate login memberships later.
CREATE ROLE lexvigil_tenant NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE lexvigil_auth NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
CREATE ROLE lexvigil_worker NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS;
GRANT USAGE ON SCHEMA lexvigil_private TO lexvigil_tenant,lexvigil_auth,lexvigil_worker;

GRANT SELECT,INSERT,DELETE ON lexvigil_private.analyses TO lexvigil_tenant;
GRANT UPDATE(saved) ON lexvigil_private.analyses TO lexvigil_tenant;
GRANT SELECT,INSERT,DELETE ON lexvigil_private.originals TO lexvigil_tenant;
GRANT SELECT,INSERT ON lexvigil_private.contract_jobs TO lexvigil_tenant;
-- This identity is supplied only by the trusted backend after verifying auth.
-- Always use set_config(..., true) inside a transaction, never session scope.
CREATE POLICY tenant_analysis_read ON lexvigil_private.analyses FOR SELECT TO lexvigil_tenant
 USING (owner = nullif(current_setting('lexvigil.owner',true),'')
        AND (saved=1 OR expires>extract(epoch FROM statement_timestamp())));
CREATE POLICY tenant_analysis_create ON lexvigil_private.analyses FOR INSERT TO lexvigil_tenant
 WITH CHECK (owner = nullif(current_setting('lexvigil.owner',true),'')
             AND status='queued' AND result IS NULL AND error IS NULL AND saved=0);
CREATE POLICY tenant_analysis_save ON lexvigil_private.analyses FOR UPDATE TO lexvigil_tenant
 USING (owner = nullif(current_setting('lexvigil.owner',true),'') AND status='completed'
        AND (saved=1 OR expires>extract(epoch FROM statement_timestamp())))
 WITH CHECK (owner = nullif(current_setting('lexvigil.owner',true),''));
CREATE POLICY tenant_analysis_delete ON lexvigil_private.analyses FOR DELETE TO lexvigil_tenant
 USING (owner = nullif(current_setting('lexvigil.owner',true),''));

CREATE POLICY tenant_original_read ON lexvigil_private.originals FOR SELECT TO lexvigil_tenant
 USING (owner = nullif(current_setting('lexvigil.owner',true),'')
        AND expires>extract(epoch FROM statement_timestamp())
        AND EXISTS (SELECT 1 FROM lexvigil_private.analyses a WHERE a.id=analysis_id AND a.owner=originals.owner));
CREATE POLICY tenant_original_create ON lexvigil_private.originals FOR INSERT TO lexvigil_tenant
 WITH CHECK (owner = nullif(current_setting('lexvigil.owner',true),'')
             AND EXISTS (SELECT 1 FROM lexvigil_private.analyses a WHERE a.id=analysis_id AND a.owner=originals.owner));
CREATE POLICY tenant_original_delete ON lexvigil_private.originals FOR DELETE TO lexvigil_tenant
 USING (owner = nullif(current_setting('lexvigil.owner',true),''));
CREATE POLICY tenant_job_read ON lexvigil_private.contract_jobs FOR SELECT TO lexvigil_tenant
 USING (owner = nullif(current_setting('lexvigil.owner',true),'')
        AND EXISTS (SELECT 1 FROM lexvigil_private.analyses a WHERE a.id=contract_jobs.id AND a.owner=contract_jobs.owner));
CREATE POLICY tenant_job_create ON lexvigil_private.contract_jobs FOR INSERT TO lexvigil_tenant
 WITH CHECK (owner = nullif(current_setting('lexvigil.owner',true),'')
             AND state='queued' AND attempts=0 AND lease_token IS NULL AND lease_until=0
             AND EXISTS (SELECT 1 FROM lexvigil_private.originals o WHERE o.analysis_id=contract_jobs.id AND o.owner=contract_jobs.owner));

GRANT SELECT,INSERT,DELETE ON lexvigil_private.sessions,lexvigil_private.auth_flows TO lexvigil_auth;
CREATE POLICY auth_session_access ON lexvigil_private.sessions FOR ALL TO lexvigil_auth USING (true) WITH CHECK (true);
CREATE POLICY auth_flow_access ON lexvigil_private.auth_flows FOR ALL TO lexvigil_auth USING (true) WITH CHECK (true);

GRANT SELECT,DELETE ON lexvigil_private.analyses,lexvigil_private.originals,lexvigil_private.contract_jobs TO lexvigil_worker;
GRANT UPDATE(status,result,error) ON lexvigil_private.analyses TO lexvigil_worker;
GRANT UPDATE(state,attempts,lease_token,lease_until) ON lexvigil_private.contract_jobs TO lexvigil_worker;
CREATE POLICY worker_analysis_access ON lexvigil_private.analyses FOR ALL TO lexvigil_worker USING (true) WITH CHECK (true);
CREATE POLICY worker_original_access ON lexvigil_private.originals FOR ALL TO lexvigil_worker USING (true) WITH CHECK (true);
CREATE POLICY worker_job_access ON lexvigil_private.contract_jobs FOR ALL TO lexvigil_worker USING (true) WITH CHECK (true);
-- RLS policies do not confer SQL privileges: worker cannot insert originals,
-- change ownership/retention, create schema objects or access auth records.

