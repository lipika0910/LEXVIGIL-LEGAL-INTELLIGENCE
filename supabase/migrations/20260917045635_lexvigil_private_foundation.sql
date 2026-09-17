-- Hosted foundation only; application-role grants and adapters follow separately.
CREATE SCHEMA lexvigil_private;
REVOKE ALL ON SCHEMA lexvigil_private FROM PUBLIC, anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA lexvigil_private REVOKE ALL ON TABLES FROM PUBLIC, anon, authenticated, service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA lexvigil_private REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC, anon, authenticated, service_role;

CREATE TABLE lexvigil_private.analyses (
 id TEXT PRIMARY KEY,
 owner TEXT NOT NULL CHECK (owner ~ '^supabase:[0-9a-f-]{36}$'),
 status TEXT NOT NULL CHECK (status IN ('queued','processing','completed','failed')),
 title TEXT NOT NULL,
 kind TEXT NOT NULL CHECK (kind IN ('contract','disputes','research')),
 result TEXT, error TEXT,
 saved INTEGER NOT NULL DEFAULT 0 CHECK (saved IN (0,1)),
 created DOUBLE PRECISION NOT NULL CHECK (created > 0 AND created < 'Infinity'::float8),
 expires DOUBLE PRECISION NOT NULL CHECK (expires >= created AND expires < 'Infinity'::float8),
 UNIQUE (id,owner)
);
CREATE INDEX analyses_owner_created_idx ON lexvigil_private.analyses(owner,created DESC);
CREATE INDEX analyses_temporary_expiry_idx ON lexvigil_private.analyses(expires) WHERE saved=0;

CREATE TABLE lexvigil_private.sessions (
 token TEXT PRIMARY KEY CHECK (token ~ '^[0-9a-f]{64}$'),
 owner TEXT NOT NULL CHECK (owner ~ '^supabase:[0-9a-f-]{36}$'),
 expires DOUBLE PRECISION NOT NULL CHECK (expires > 0 AND expires < 'Infinity'::float8)
);
CREATE INDEX sessions_expiry_idx ON lexvigil_private.sessions(expires);
CREATE INDEX sessions_owner_idx ON lexvigil_private.sessions(owner);
CREATE TABLE lexvigil_private.auth_flows (
 token TEXT PRIMARY KEY CHECK (token ~ '^[0-9a-f]{64}$'),
 verifier TEXT NOT NULL, purpose TEXT NOT NULL,
 expires DOUBLE PRECISION NOT NULL CHECK (expires > 0 AND expires < 'Infinity'::float8)
);
CREATE INDEX auth_flows_expiry_idx ON lexvigil_private.auth_flows(expires);

-- Only authenticated ciphertext format is accepted, never plaintext originals.
CREATE TABLE lexvigil_private.originals (
 analysis_id TEXT PRIMARY KEY, owner TEXT NOT NULL, filename TEXT NOT NULL,
 payload BYTEA NOT NULL,
 size INTEGER NOT NULL CHECK (size > 0 AND size <= 15728640),
 sha256 TEXT NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
 consent_version TEXT NOT NULL CHECK (consent_version='original-48h-v1'),
 consented_at DOUBLE PRECISION NOT NULL CHECK (consented_at > 0 AND consented_at < 'Infinity'::float8),
 expires DOUBLE PRECISION NOT NULL,
 encryption_version INTEGER NOT NULL CHECK (encryption_version=1),
 FOREIGN KEY (analysis_id,owner) REFERENCES lexvigil_private.analyses(id,owner) ON DELETE CASCADE,
 CHECK (expires >= consented_at AND expires <= consented_at + 172800),
 CHECK (octet_length(payload)=size+34),
 CHECK (substring(payload FROM 1 FOR 6)=decode('4c56454e4331','hex'))
);
CREATE INDEX originals_expiry_idx ON lexvigil_private.originals(expires);
CREATE INDEX originals_owner_idx ON lexvigil_private.originals(owner);
CREATE TABLE lexvigil_private.contract_jobs (
 id TEXT PRIMARY KEY, owner TEXT NOT NULL, as_of TEXT NOT NULL, ocr_language TEXT NOT NULL,
 state TEXT NOT NULL CHECK (state IN ('queued','running','failed','cancelled','done')),
 attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts BETWEEN 0 AND 3),
 lease_token TEXT,
 lease_until DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (lease_until >= 0 AND lease_until < 'Infinity'::float8),
 created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 FOREIGN KEY (id,owner) REFERENCES lexvigil_private.analyses(id,owner) ON DELETE CASCADE
);
CREATE INDEX contract_jobs_claim_idx ON lexvigil_private.contract_jobs(state,lease_until,created_at);
CREATE INDEX contract_jobs_owner_idx ON lexvigil_private.contract_jobs(owner);

CREATE FUNCTION lexvigil_private.protect_original_retention() RETURNS trigger
LANGUAGE plpgsql SECURITY INVOKER SET search_path = '' AS $$
BEGIN
 IF NEW.consented_at IS DISTINCT FROM OLD.consented_at
 OR NEW.consent_version IS DISTINCT FROM OLD.consent_version
 OR NEW.owner IS DISTINCT FROM OLD.owner
 OR NEW.analysis_id IS DISTINCT FROM OLD.analysis_id
 OR NEW.expires > OLD.expires THEN
  RAISE EXCEPTION 'Original ownership, consent and maximum retention are immutable';
 END IF;
 RETURN NEW;
END;
$$;
CREATE TRIGGER originals_retention_guard BEFORE UPDATE ON lexvigil_private.originals
FOR EACH ROW EXECUTE FUNCTION lexvigil_private.protect_original_retention();

ALTER TABLE lexvigil_private.analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE lexvigil_private.analyses FORCE ROW LEVEL SECURITY;
ALTER TABLE lexvigil_private.sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE lexvigil_private.sessions FORCE ROW LEVEL SECURITY;
ALTER TABLE lexvigil_private.auth_flows ENABLE ROW LEVEL SECURITY;
ALTER TABLE lexvigil_private.auth_flows FORCE ROW LEVEL SECURITY;
ALTER TABLE lexvigil_private.originals ENABLE ROW LEVEL SECURITY;
ALTER TABLE lexvigil_private.originals FORCE ROW LEVEL SECURITY;
ALTER TABLE lexvigil_private.contract_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE lexvigil_private.contract_jobs FORCE ROW LEVEL SECURITY;
REVOKE ALL ON ALL TABLES IN SCHEMA lexvigil_private FROM PUBLIC, anon, authenticated, service_role;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA lexvigil_private FROM PUBLIC, anon, authenticated, service_role;
-- No permissive RLS policies: browser/client roles have no access.

