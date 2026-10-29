"""Fail-closed hosted-demo bootstrap; no dotenv loading or startup DDL."""
import os
from pathlib import Path
from urllib.parse import urlsplit
from .hosted_connections import create_hosted_transactions, PROJECT
from .managed_auth import ManagedAuth
from .showcase_api import create_showcase_app
from .showcase_processing import process_contract

ROOT = Path(__file__).resolve().parent.parent


def validate_environment(env):
    if env.get('LEXVIGIL_RELEASE_PROFILE') != 'showcase':
        raise ValueError('Hosted entry requires the showcase release profile.')
    if env.get('SUPABASE_URL') != 'https://' + PROJECT + '.supabase.co':
        raise ValueError('Hosted entry requires the approved Mumbai Supabase project.')
    origin = env.get('APP_ORIGIN', '')
    try:
        parsed = urlsplit(origin)
        valid = (parsed.scheme == 'https' and parsed.hostname and
                 not parsed.username and not parsed.password and not parsed.path and
                 not parsed.query and not parsed.fragment and parsed.port in (None,443)
                 and not any(c.isspace() for c in origin))
    except ValueError:
        valid = False
    if not valid:
        raise ValueError('APP_ORIGIN requires an explicit HTTPS origin without a path.')
    if env.get('VERCEL') == '1' and env.get('VERCEL_REGION') != 'bom1':
        raise ValueError('Hosted execution is restricted to the Mumbai region.')
    key = env.get('SUPABASE_PUBLISHABLE_KEY', '')
    if not key.startswith('sb_publishable_') or any(c.isspace() for c in key):
        raise ValueError('A Supabase publishable key is required.')
    passwords = {cap: env.get('LEXVIGIL_DB_' + cap.upper() + '_PASSWORD', '')
                 for cap in ('tenant','auth','worker')}
    if any(len(p)<24 or '\x00' in p for p in passwords.values()) or len(set(passwords.values())) != 3:
        raise ValueError('Three distinct restricted runtime passwords are required.')
    approved_origins = {origin}
    preview_host = env.get('VERCEL_URL', '').strip()
    if preview_host:
        candidate = ('https://' + preview_host) if '://' not in preview_host else preview_host
        parsed_preview = urlsplit(candidate)
        valid_preview = (env.get('VERCEL') == '1' and env.get('VERCEL_ENV') == 'preview' and
                         parsed_preview.scheme == 'https' and parsed_preview.hostname and
                         parsed_preview.hostname.startswith('lexvigil-') and
                         parsed_preview.hostname.endswith('.vercel.app') and
                         not parsed_preview.username and not parsed_preview.password and
                         not parsed_preview.path and not parsed_preview.query and
                         not parsed_preview.fragment and parsed_preview.port in (None, 443))
        if not valid_preview:
            raise ValueError('Preview origin is not an approved LexVigil Vercel deployment.')
        approved_origins.add(candidate.rstrip('/'))
    # Return secrets only to the in-process constructor; never log this value.
    return origin, key, passwords, approved_origins


def build_showcase_app(env=None, *, transactions_factory=create_hosted_transactions,
                       provider_factory=ManagedAuth, app_factory=create_showcase_app):
    config = os.environ if env is None else env
    origin, key, passwords, approved_origins = validate_environment(config)
    provider = provider_factory(config['SUPABASE_URL'], key)
    transactions = transactions_factory(passwords, ROOT / 'prod-ca-2021.crt')
    try:
        return app_factory(transactions, provider, origin, process_contract,
                           allowed_origins=approved_origins)
    except Exception:
        for engine in transactions.engines.values():
            engine.dispose()
        raise RuntimeError('Hosted application setup failed.') from None
