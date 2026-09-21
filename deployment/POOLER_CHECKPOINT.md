# LexVigil session-pooler checkpoint

User-supplied connection metadata (2026-09-19):

- Host: `aws-0-ap-south-1.pooler.supabase.com`
- Port: `5432`
- Database: `postgres`
- Administrative username: `postgres.mbnwdfdxksiuptwonjev`
- Selected project: `mbnwdfdxksiuptwonjev`

No password was provided or requested in chat. These values alone are not
usable application credentials. The administrative username must not be
used by the deployed application's runtime adapters.

## Checks performed

A bounded, credential-free PostgreSQL SSLRequest reached this host and port
and received the TLS-supported response. Certificate validation using this
machine's Python default trust store then failed with
`self-signed certificate in certificate chain`. No authentication attempt
was made and verification was not disabled. Reachability does not prove
that the pooler can authenticate this project's username.

An independent authenticated Supabase connector query confirmed database
`postgres`, no `lexvigil_private` schema, and none of the three planned
LexVigil capability roles on the selected project. This connector check is
not evidence of a working application pooler connection.

## Next prerequisite

Obtain the database CA certificate through this project's Supabase dashboard
Database settings. Configure it explicitly as the trusted root and repeat
hostname-verified TLS validation before sending database credentials.
Do not trust a certificate extracted from the failed connection itself.

Official guidance:
https://supabase.com/docs/guides/platform/ssl-enforcement
https://supabase.com/docs/guides/database/psql

After verified TLS, provision dedicated least-privilege login credentials
through a secure local/deployment secret workflow, apply and verify the
private schema on the selected project, and test the actual adapters.
No hosted schema, Auth configuration, billing, or deployment was changed
by these checks.
