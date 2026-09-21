# Verified pooler TLS

On 2026-09-19, the user-provided `prod-ca-2021.crt` successfully verified
the certificate chain and hostname for
`aws-0-ap-south-1.pooler.supabase.com:5432` using Python's standard SSL
client with explicit `cafile` and normal hostname verification enabled.
The negotiated protocol was TLS 1.3. This resolves the default-trust-store
failure recorded in POOLER_CHECKPOINT.md.

CA subject: Supabase Root 2021 CA, Supabase Inc.
CA expiry: 2031-04-26 10:56:53 UTC.
CA SHA-256 fingerprint:
`807025ad50d4ed219d2c9c7d299c004f824eb00cf7f65afef607d07b72e6cafa`.

The supplied file parsed as a CA certificate, with no private-key marker.
No passwords were used, no database authentication was attempted, and no
database objects, Auth settings, billing, or deployment configuration were
changed. This test establishes verified transport, not successful login,
project routing, role isolation, or application readiness.

Future psycopg connections must explicitly use `sslmode=verify-full` and
`sslrootcert` pointing to this CA file (with a valid deployment-specific
path). Do not fall back to unverified SSL. Keep administrative credentials
out of the deployed application; provision separate restricted runtime
logins and verify their behavior before enabling the hosted adapters.
