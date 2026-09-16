"""Fail-closed production configuration validation; never echoes secret values."""
import base64
import ipaddress
from urllib.parse import urlsplit
from sqlalchemy.engine import make_url

DEVELOPMENT_PROJECT = 'mbnwdfdxksiuptwonjev'


def production_errors(env):
    if env.get('LEXVIGIL_ENV') != 'production':
        return []
    errors = []
    if env.get('AUTH_PROVIDER') != 'supabase':
        errors.append('Production requires AUTH_PROVIDER=supabase; local accounts are development-only.')
    try:
        origin = urlsplit(env.get('APP_ORIGIN', ''))
        valid = (origin.scheme == 'https' and origin.hostname and not origin.username
                 and not origin.password and not origin.path and not origin.query and not origin.fragment
                 and origin.port in (None, 443) and origin.hostname not in ('localhost', 'localhost.localdomain'))
        try:
            valid = valid and ipaddress.ip_address(origin.hostname).is_global
        except ValueError:
            pass
        if not valid:
            raise ValueError()
    except (ValueError, TypeError):
        errors.append('Production APP_ORIGIN must be a public HTTPS origin without a path, query or credentials.')
    try:
        url = make_url(env.get('DATABASE_URL', ''))
        if (url.drivername != 'postgresql+psycopg' or not url.host or not url.database
                or not url.username or not url.password or url.query.get('sslmode') != 'verify-full'):
            raise ValueError()
    except Exception:
        errors.append('Production requires a PostgreSQL psycopg URL with credentials and sslmode=verify-full.')
    try:
        project = urlsplit(env.get('SUPABASE_URL', ''))
        if (project.scheme != 'https' or not project.hostname or project.username or project.password
                or project.path not in ('', '/') or project.query or project.fragment or project.port not in (None, 443)):
            raise ValueError()
        if project.hostname == DEVELOPMENT_PROJECT + '.supabase.co':
            errors.append('The dedicated LexVigil development Supabase project cannot be used for production.')
    except ValueError:
        errors.append('Production requires a valid HTTPS SUPABASE_URL.')
    key = env.get('SUPABASE_PUBLISHABLE_KEY', '')
    if not key.startswith('sb_publishable_') or any(c.isspace() for c in key):
        errors.append('Production requires the server-side Supabase publishable-key configuration, not a secret/service-role key.')
    try:
        key_bytes = base64.b64decode(env.get('ORIGINAL_ENCRYPTION_KEY', ''), validate=True)
        if len(key_bytes) != 32 or len(set(key_bytes)) < 8:
            raise ValueError()
    except ValueError:
        errors.append('Production requires a securely generated 32-byte base64 ORIGINAL_ENCRYPTION_KEY with an approved recovery plan.')
    if env.get('WEB_CONCURRENCY', '1') != '1':
        errors.append('Multiple API processes are blocked until shared quotas and the production queue are implemented.')
    return errors


def validate_environment(env):
    # Vercel preview deployments are public-hosted environments too. This API
    # currently depends on process-resident workers and SQLite-only adapters;
    # refuse startup BEFORE app.py creates any tables or local accounts. A
    # production flag alone does not make this architecture serverless-safe.
    if env.get('VERCEL') == '1' or env.get('VERCEL_ENV') in ('preview', 'production'):
        raise RuntimeError(
            'The current LexVigil API cannot run on Vercel Functions: hosted storage, '
            'durable job dispatch and bounded OCR execution must be implemented and '
            'verified first. Do not bypass this guard with development settings.'
        )
    if env.get('LEXVIGIL_ENV', 'development') not in ('development', 'test', 'production'):
        raise RuntimeError('LEXVIGIL_ENV must be development, test or production. Use production security settings for staging.')
    errors = production_errors(env)
    if errors:
        raise RuntimeError('Invalid production configuration: ' + ' '.join(errors))
