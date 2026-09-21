"""Bounded, verified connections for the explicitly selected Mumbai demo.

This factory is not wired into app.py until hosted adapters are complete.
Passwords must come from a server-side secret store, never client input.
"""
from pathlib import Path
import ssl

from sqlalchemy import create_engine
from sqlalchemy.engine import URL

from backend.hosted_transactions import HostedTransactions, ROLES

PROJECT = 'mbnwdfdxksiuptwonjev'
POOLER = 'aws-0-ap-south-1.pooler.supabase.com'
LOGIN_ROLES = {cap: f'lexvigil_{cap}_login' for cap in ROLES}


def create_hosted_transactions(passwords, ca_file, *, engine_factory=create_engine):
    """Validate all configuration before constructing three separate pools.

    Catalog checks inside HostedTransactions remain mandatory: an allowed
    login name alone does not establish least-privilege database permissions.
    """
    if not isinstance(passwords, dict) or set(passwords) != set(ROLES):
        raise ValueError('Separate tenant, auth and worker passwords are required.')
    if any(not isinstance(p, str) or len(p) < 24 or '\x00' in p
           for p in passwords.values()):
        raise ValueError('Runtime passwords must contain at least 24 characters.')
    if len(set(passwords.values())) != 3:
        raise ValueError('Runtime capabilities must use distinct passwords.')
    try:
        ca_path = Path(ca_file).resolve(strict=True)
        ssl.create_default_context(cafile=str(ca_path))
    except (OSError, ValueError, TypeError, ssl.SSLError):
        raise ValueError('A readable, valid trusted CA file is required.') from None

    engines = {}
    try:
        for cap in ROLES:
            url = URL.create('postgresql+psycopg',
                             username=LOGIN_ROLES[cap] + '.' + PROJECT,
                             password=passwords[cap], host=POOLER,
                             port=5432, database='postgres')
            engines[cap] = engine_factory(
                url, echo=False, hide_parameters=True,
                pool_size=1, max_overflow=0, pool_timeout=5,
                pool_recycle=300, pool_pre_ping=True,
                connect_args={'sslmode': 'verify-full',
                              'sslrootcert': str(ca_path),
                              'connect_timeout': 10,
                              'prepare_threshold': None,
                              'application_name': 'lexvigil-' + cap,
                              'options': '-c statement_timeout=5000 -c idle_in_transaction_session_timeout=10000'},
            )
        return HostedTransactions(engines)
    except Exception:
        for engine in engines.values():
            engine.dispose()
        # Construction errors can include connection configuration. Keep the
        # public exception independent of any driver-provided message.
        raise RuntimeError('Hosted connection setup failed.') from None
