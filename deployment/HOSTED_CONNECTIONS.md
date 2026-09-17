# Hosted transaction integration checkpoint

`backend/hosted_transactions.py` introduces an explicit capability boundary for PostgreSQL adapters. It is not yet wired into the FastAPI application. Existing SQLite development behavior is unchanged.

The constructor requires distinct tenant/auth/worker engines. Every transaction checks the connecting role's catalog flags and memberships, rejects administrator/high-privilege or mixed-capability credentials, assumes only the fixed capability role, sets a private search path, bounds statement/lock waits, and uses transaction-local parameter-bound owner context. The context manager delegates commit/rollback and connection return to SQLAlchemy.

Callers must supply a canonical owner derived from verified Supabase authentication. A canonical UUID is not proof of authentication. The module must never receive an owner directly from client input. RLS cannot protect against a trusted database client intentionally changing its owner setting.

## Evidence and limits

23 unit tests passed for invalid identity rejection, per-transaction binding, privileged/mixed-role rejection before body execution, separate engine requirements, auth/worker owner clearing and rollback paths. These tests use fake engines and do not establish real pool behavior or network/TLS correctness. Hosted SQL role-isolation tests are separately recorded in supabase/RUNTIME_ROLES.md.

## Still required

1. Provision three separate low-privilege login roles in the demo project and store their passwords only in an approved secret store. Each login needs exactly one capability role and permission to SET ROLE. Never use postgres, service-role credentials or the development project's credentials for runtime access.
2. Construct TLS-verified psycopg connections with bounded pool sizes and connection timeouts. Verify account context isolation across real reused connections, commit/rollback/error paths and concurrent accounts.
3. Refactor API/auth/storage/queue operations to select the correct capability and explicit verified identity. Remove hosted startup DDL and implement shared quotas and leased jobs. No deployment guard should be removed before this succeeds.
4. Test the actual Vercel runtime and free-tier limits. The new helper alone does not make the backend serverless-compatible.

Do not paste database passwords into chat or commit environment files. No new credentials were generated or used for this checkpoint.
