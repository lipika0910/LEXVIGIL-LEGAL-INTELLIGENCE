"""Explicit, transaction-local capability boundary for forthcoming PG adapters.

Callers must pass a Supabase-verified owner, never a request-supplied owner.
This module does not authenticate users or provision database credentials.
"""
from contextlib import contextmanager
from uuid import UUID
from sqlalchemy import text

ROLES = {'tenant': 'lexvigil_tenant', 'auth': 'lexvigil_auth', 'worker': 'lexvigil_worker'}


def canonical_owner(value):
    if not isinstance(value, str) or not value.startswith('supabase:'):
        raise ValueError('A verified Supabase owner is required.')
    try:
        normalized = 'supabase:' + str(UUID(value[9:]))
    except (ValueError, AttributeError):
        raise ValueError('A verified Supabase owner is required.') from None
    if normalized != value:
        raise ValueError('The verified owner must use a canonical UUID.')
    return normalized


class HostedTransactions:
    def __init__(self, engines):
        if set(engines) != set(ROLES):
            raise ValueError('Separate tenant, auth and worker engines are required.')
        if len({id(engine) for engine in engines.values()}) != 3:
            raise ValueError('Capability engines must not be shared.')
        if any(engine.dialect.name != 'postgresql' for engine in engines.values()):
            raise ValueError('Hosted transactions require PostgreSQL.')
        self.engines = dict(engines)

    @contextmanager
    def transaction(self, capability, owner=None):
        if capability not in ROLES:
            raise ValueError('Unknown database capability.')
        identity = canonical_owner(owner) if capability == 'tenant' else ''
        if capability != 'tenant' and owner is not None:
            raise ValueError('Account context is only valid for tenant transactions.')
        with self.engines[capability].begin() as connection:
            # Read catalog using explicit schema qualification, before SET ROLE.
            record = connection.execute(text('''
                SELECT r.rolcanlogin, r.rolsuper, r.rolbypassrls,
                       r.rolcreaterole, r.rolcreatedb, r.rolreplication,
                       current_user = session_user AS unchanged,
                       pg_catalog.pg_has_role(session_user, 'postgres', 'MEMBER') AS administrator,
                       pg_catalog.pg_has_role(session_user, 'lexvigil_tenant', 'MEMBER') AS tenant,
                       pg_catalog.pg_has_role(session_user, 'lexvigil_auth', 'MEMBER') AS auth,
                       pg_catalog.pg_has_role(session_user, 'lexvigil_worker', 'MEMBER') AS worker
                FROM pg_catalog.pg_roles r WHERE r.rolname = session_user
            ''')).mappings().one()
            unsafe = (not record['rolcanlogin'] or not record['unchanged'] or
                      any(record[key] for key in ('rolsuper', 'rolbypassrls', 'rolcreaterole',
                                                   'rolcreatedb', 'rolreplication', 'administrator')))
            if unsafe or any(bool(record[key]) != (key == capability) for key in ROLES):
                raise RuntimeError('Unsafe database credential capability; transaction refused.')
            # Role names are fixed constants, not interpolated request values.
            connection.execute(text('SET LOCAL ROLE ' + ROLES[capability]))
            connection.execute(text('SET LOCAL search_path = pg_catalog, lexvigil_private'))
            connection.execute(text('SET LOCAL statement_timeout = 5000'))
            connection.execute(text('SET LOCAL lock_timeout = 2000'))
            connection.execute(text("SELECT pg_catalog.set_config('lexvigil.owner', :owner, true)"),
                               {'owner': identity})
            yield connection
