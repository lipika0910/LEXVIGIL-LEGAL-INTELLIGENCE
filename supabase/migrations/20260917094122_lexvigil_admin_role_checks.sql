-- Administrative role-assumption for maintenance/testing; not an application login.
-- No automatic privilege inheritance and no role-administration delegation.
GRANT lexvigil_tenant, lexvigil_auth, lexvigil_worker TO postgres WITH INHERIT FALSE, SET TRUE, ADMIN FALSE;

