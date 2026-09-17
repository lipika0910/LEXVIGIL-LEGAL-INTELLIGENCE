BEGIN;
INSERT INTO lexvigil_private.analyses(id,owner,status,title,kind,created,expires,saved)
SELECT id,owner,'completed','Synthetic RLS check','contract',extract(epoch FROM now())-100,
 extract(epoch FROM now())+delta,saved
FROM (VALUES
 ('rls-a','supabase:00000000-0000-4000-8000-000000000001',1000,0),
 ('rls-b','supabase:00000000-0000-4000-8000-000000000002',1000,0),
 ('rls-expired','supabase:00000000-0000-4000-8000-000000000001',-1,0),
 ('rls-saved','supabase:00000000-0000-4000-8000-000000000001',-1,1)
) AS v(id,owner,delta,saved);
SET LOCAL ROLE lexvigil_tenant;
SELECT set_config('lexvigil.owner','',true);
DO $$ BEGIN
 IF EXISTS (SELECT 1 FROM lexvigil_private.analyses) THEN RAISE EXCEPTION 'Missing identity exposed data'; END IF;
END $$;
SELECT set_config('lexvigil.owner','supabase:00000000-0000-4000-8000-000000000001',true);
DO $$
DECLARE affected integer;
BEGIN
 IF (SELECT count(*) FROM lexvigil_private.analyses) <> 2 THEN RAISE EXCEPTION 'Owner/expiry filtering failed'; END IF;
 UPDATE lexvigil_private.analyses SET saved=1 WHERE id='rls-b';
 GET DIAGNOSTICS affected=ROW_COUNT;
 IF affected<>0 THEN RAISE EXCEPTION 'Cross-owner update succeeded'; END IF;
 UPDATE lexvigil_private.analyses SET saved=1 WHERE id='rls-a';
 GET DIAGNOSTICS affected=ROW_COUNT;
 IF affected<>1 THEN RAISE EXCEPTION 'Own save failed'; END IF;
 BEGIN
  UPDATE lexvigil_private.analyses SET result='forged' WHERE id='rls-a';
  RAISE EXCEPTION 'Tenant could publish result';
 EXCEPTION WHEN insufficient_privilege THEN NULL;
 END;
 BEGIN
  UPDATE lexvigil_private.analyses SET owner='supabase:00000000-0000-4000-8000-000000000002' WHERE id='rls-a';
  RAISE EXCEPTION 'Tenant could reassign owner';
 EXCEPTION WHEN insufficient_privilege THEN NULL;
 END;
 BEGIN
  INSERT INTO lexvigil_private.analyses(id,owner,status,title,kind,created,expires)
  VALUES ('rls-forged','supabase:00000000-0000-4000-8000-000000000002','queued','Synthetic','contract',1,2);
  RAISE EXCEPTION 'Cross-owner insert succeeded';
 EXCEPTION WHEN insufficient_privilege THEN NULL;
 END;
 BEGIN
  PERFORM * FROM lexvigil_private.sessions;
  RAISE EXCEPTION 'Tenant could read sessions';
 EXCEPTION WHEN insufficient_privilege THEN NULL;
 END;
 BEGIN
  EXECUTE 'TRUNCATE lexvigil_private.analyses CASCADE';
  RAISE EXCEPTION 'Tenant could truncate';
 EXCEPTION WHEN insufficient_privilege THEN NULL;
 END;
END $$;
SELECT set_config('lexvigil.owner','supabase:00000000-0000-4000-8000-000000000002',true);
DO $$ BEGIN
 IF (SELECT count(*) FROM lexvigil_private.analyses)<>1 OR NOT EXISTS(SELECT 1 FROM lexvigil_private.analyses WHERE id='rls-b')
 THEN RAISE EXCEPTION 'Account context switch leaked records'; END IF;
END $$;
RESET ROLE;
SET LOCAL ROLE lexvigil_worker;
DO $$ BEGIN
 IF (SELECT count(*) FROM lexvigil_private.analyses)<>4 THEN RAISE EXCEPTION 'Worker cannot see cleanup candidates'; END IF;
 UPDATE lexvigil_private.analyses SET status='failed',error='Synthetic test' WHERE id='rls-b';
 BEGIN
  PERFORM * FROM lexvigil_private.auth_flows;
  RAISE EXCEPTION 'Worker could read auth flows';
 EXCEPTION WHEN insufficient_privilege THEN NULL;
 END;
 BEGIN
  UPDATE lexvigil_private.analyses SET saved=1 WHERE id='rls-b';
  RAISE EXCEPTION 'Worker could change user save choice';
 EXCEPTION WHEN insufficient_privilege THEN NULL;
 END;
END $$;
RESET ROLE;
SET LOCAL ROLE lexvigil_auth;
DO $$ BEGIN
 BEGIN
  PERFORM * FROM lexvigil_private.analyses;
  RAISE EXCEPTION 'Auth role could read contracts';
 EXCEPTION WHEN insufficient_privilege THEN NULL;
 END;
 INSERT INTO lexvigil_private.sessions VALUES(repeat('a',64),'supabase:00000000-0000-4000-8000-000000000001',extract(epoch FROM now())+60);
END $$;
RESET ROLE;
ROLLBACK;
DO $$ BEGIN
 IF nullif(current_setting('lexvigil.owner',true),'') IS NOT NULL THEN RAISE EXCEPTION 'Transaction identity leaked'; END IF;
 IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname IN ('lexvigil_tenant','lexvigil_auth','lexvigil_worker')
           AND (rolcanlogin OR rolsuper OR rolbypassrls OR rolcreaterole OR rolcreatedb)) THEN RAISE EXCEPTION 'Unsafe role capability'; END IF;
END $$;
SELECT 'passed: tenant isolation, expiry, context reset, field privileges, auth/worker separation; synthetic writes rolled back' AS result;

