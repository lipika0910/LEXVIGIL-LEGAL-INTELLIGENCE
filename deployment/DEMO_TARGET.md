# Current hosted-demo target

User decision, 2026-09-19: use the existing **LexVigil** Supabase project
`mbnwdfdxksiuptwonjev` for the personal, non-commercial demonstration.
This supersedes the earlier development-only target decision for this demo;
it does not authorize treating a shared development/demo environment as an
isolated production environment.

Read-only connector checks confirmed ACTIVE_HEALTHY in Mumbai (`ap-south-1`).
The `public` and `lexvigil_private` table listing was empty and migration
history was empty. These checks do not imply that Auth has no users or that
Storage contains no objects. Preserve existing accounts and OAuth settings.

The separate `LexVigil Demo` project `rhtbctgvqpvmiqmnegwh` remains untouched.
Its hosted migrations and SQL verification results do not apply to the newly
selected project. No schema migration, runtime credential creation, billing
change, or deployment was performed as part of this target selection.

The supplied HTTPS project URL is an Auth/Data API endpoint, not a PostgreSQL
connection string. The current backend design still needs verified database
connection details and separate least-privilege runtime logins. Do not use an
administrator password for application runtime connections or paste secrets
into chat.

Existing deployment guards remain enabled until the database adapters, role
isolation, hosted runtime and retention behavior pass integration tests. A
future explicit demo configuration must distinguish this approved shared
demo target from a genuinely isolated production deployment.

The fully-free and India-only AI requirements remain unchanged. Mumbai
database placement alone does not establish the location or price of AI
inference, frontend hosting, or other services.
