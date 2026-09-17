BEGIN;
DO $$
DECLARE
 a text := 'supabase:00000000-0000-4000-8000-000000000001';
 b text := 'supabase:00000000-0000-4000-8000-000000000002';
BEGIN
 IF (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
     WHERE n.nspname='lexvigil_private' AND c.relkind='r' AND c.relrowsecurity AND c.relforcerowsecurity) <> 5 THEN
  RAISE EXCEPTION 'RLS enforcement missing';
 END IF;
 INSERT INTO lexvigil_private.analyses(id,owner,status,title,kind,created,expires)
 VALUES ('migration-check',a,'queued','Synthetic schema check','contract',1000,87400);
 BEGIN
  INSERT INTO lexvigil_private.contract_jobs(id,owner,as_of,ocr_language,state)
  VALUES ('migration-check',b,'','eng','queued');
  RAISE EXCEPTION 'Cross-owner job was accepted';
 EXCEPTION WHEN foreign_key_violation THEN NULL;
 END;
 BEGIN
  INSERT INTO lexvigil_private.originals VALUES
   ('migration-check',a,'synthetic.txt',decode('4c56454e4331','hex')||decode(repeat('00',29),'hex'),1,repeat('0',64),'original-48h-v1',1000,173801,1);
  RAISE EXCEPTION 'Overlong original retention was accepted';
 EXCEPTION WHEN check_violation THEN NULL;
 END;
 INSERT INTO lexvigil_private.originals VALUES
  ('migration-check',a,'synthetic.txt',decode('4c56454e4331','hex')||decode(repeat('00',29),'hex'),1,repeat('0',64),'original-48h-v1',1000,2000,1);
 BEGIN
  UPDATE lexvigil_private.originals SET expires=2001 WHERE analysis_id='migration-check';
  RAISE EXCEPTION 'Retention extension was accepted';
 EXCEPTION WHEN raise_exception THEN
  IF SQLERRM <> 'Original ownership, consent and maximum retention are immutable' THEN RAISE; END IF;
 END;
 BEGIN
  UPDATE lexvigil_private.originals SET consented_at=1001 WHERE analysis_id='migration-check';
  RAISE EXCEPTION 'Consent clock change was accepted';
 EXCEPTION WHEN raise_exception THEN
  IF SQLERRM <> 'Original ownership, consent and maximum retention are immutable' THEN RAISE; END IF;
 END;
 UPDATE lexvigil_private.analyses SET saved=1 WHERE id='migration-check';
 IF (SELECT expires FROM lexvigil_private.originals WHERE analysis_id='migration-check') <> 2000 THEN
  RAISE EXCEPTION 'Saving report extended original retention';
 END IF;
 INSERT INTO lexvigil_private.contract_jobs(id,owner,as_of,ocr_language,state)
 VALUES ('migration-check',a,'','eng','queued');
 DELETE FROM lexvigil_private.analyses WHERE id='migration-check';
 IF EXISTS(SELECT 1 FROM lexvigil_private.originals WHERE analysis_id='migration-check')
 OR EXISTS(SELECT 1 FROM lexvigil_private.contract_jobs WHERE id='migration-check') THEN
  RAISE EXCEPTION 'Dependent rows survived report deletion';
 END IF;
END;
$$;
SET LOCAL ROLE anon;
DO $$ BEGIN
 BEGIN
  PERFORM * FROM lexvigil_private.analyses;
  RAISE EXCEPTION 'Anonymous access was permitted';
 EXCEPTION WHEN insufficient_privilege THEN NULL;
 END;
END $$;
RESET ROLE;
SET LOCAL ROLE authenticated;
DO $$ BEGIN
 BEGIN
  PERFORM * FROM lexvigil_private.originals;
  RAISE EXCEPTION 'Browser authenticated access was permitted';
 EXCEPTION WHEN insufficient_privilege THEN NULL;
 END;
END $$;
RESET ROLE;
ROLLBACK;
SELECT 'passed: RLS flags, owner FK, retention checks, immutable consent, save behavior, cascading delete, anon and authenticated denial; synthetic data rolled back' AS result;

