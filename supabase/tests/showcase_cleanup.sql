BEGIN;
SELECT set_config('lexvigil.cleanup_test',gen_random_uuid()::text,true);
INSERT INTO lexvigil_private.analyses(id,owner,status,title,kind,saved,created,expires)
SELECT current_setting('lexvigil.cleanup_test')||label,
 'supabase:'||current_setting('lexvigil.cleanup_test'),status,'Synthetic cleanup rollback check','contract',saved,
 extract(epoch FROM now())-3600,
 extract(epoch FROM now())+expiry
FROM (VALUES ('expired','completed',0,-10),('saved','completed',1,-10),
 ('active','completed',0,3600),('abandoned','queued',0,3600)) v(label,status,saved,expiry);
INSERT INTO lexvigil_private.analyses(id,owner,status,title,kind,created,expires)
VALUES(current_setting('lexvigil.cleanup_test')||'recent',
 'supabase:'||current_setting('lexvigil.cleanup_test'),'queued','Synthetic recent','contract',
 extract(epoch FROM now()),extract(epoch FROM now())+3600);
INSERT INTO lexvigil_private.sessions(token,owner,expires)
SELECT repeat(md5(current_setting('lexvigil.cleanup_test')||label),2),
 'supabase:'||current_setting('lexvigil.cleanup_test'),extract(epoch FROM now())+expiry
FROM (VALUES('expired',-10),('active',3600)) v(label,expiry);
INSERT INTO lexvigil_private.auth_flows(token,verifier,purpose,expires)
SELECT repeat(md5(current_setting('lexvigil.cleanup_test')||label),2),'','synthetic-cleanup',
 extract(epoch FROM now())+expiry FROM (VALUES('expired',-10),('active',3600)) v(label,expiry);
SET LOCAL ROLE lexvigil_worker;
SELECT lexvigil_private.cleanup_reports();
DO $$
BEGIN
 IF EXISTS(SELECT 1 FROM lexvigil_private.analyses WHERE id=current_setting('lexvigil.cleanup_test')||'expired')
 THEN RAISE EXCEPTION 'Expired temporary report survived'; END IF;
 IF (SELECT count(*) FROM lexvigil_private.analyses WHERE id IN(
 current_setting('lexvigil.cleanup_test')||'saved',current_setting('lexvigil.cleanup_test')||'active'))<>2
 THEN RAISE EXCEPTION 'Saved/active report removed'; END IF;
 IF NOT EXISTS(SELECT 1 FROM lexvigil_private.analyses WHERE id=current_setting('lexvigil.cleanup_test')||'abandoned' AND status='failed')
 THEN RAISE EXCEPTION 'Abandoned report not recovered'; END IF;
 IF NOT EXISTS(SELECT 1 FROM lexvigil_private.analyses WHERE id=current_setting('lexvigil.cleanup_test')||'recent' AND status='queued')
 THEN RAISE EXCEPTION 'Fresh request was interrupted'; END IF;
END $$;
RESET ROLE;
SET LOCAL ROLE lexvigil_auth;
SELECT lexvigil_private.cleanup_auth_records();
DO $$
BEGIN
 IF EXISTS(SELECT 1 FROM lexvigil_private.sessions WHERE token=repeat(md5(current_setting('lexvigil.cleanup_test')||'expired'),2))
 OR EXISTS(SELECT 1 FROM lexvigil_private.auth_flows WHERE token=repeat(md5(current_setting('lexvigil.cleanup_test')||'expired'),2))
 THEN RAISE EXCEPTION 'Expired auth records survived'; END IF;
 IF NOT EXISTS(SELECT 1 FROM lexvigil_private.sessions WHERE token=repeat(md5(current_setting('lexvigil.cleanup_test')||'active'),2))
 OR NOT EXISTS(SELECT 1 FROM lexvigil_private.auth_flows WHERE token=repeat(md5(current_setting('lexvigil.cleanup_test')||'active'),2))
 THEN RAISE EXCEPTION 'Active auth records removed'; END IF;
END $$;
RESET ROLE;
ROLLBACK;
