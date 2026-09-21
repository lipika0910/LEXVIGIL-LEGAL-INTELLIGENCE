ALTER TABLE lexvigil_private.sessions DROP CONSTRAINT sessions_owner_check;
ALTER TABLE lexvigil_private.sessions ADD CONSTRAINT sessions_owner_check CHECK (owner ~ '^(recovery:)?supabase:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$');
