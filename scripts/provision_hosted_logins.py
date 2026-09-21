"""Explicit local setup/check of LexVigil runtime logins; never prints secrets.

Run as a module from the repository root. --activate only activates NOLOGIN
roles; it never resets an already-active login's password. Windows DPAPI
protects the local credential bundle. Production secret delivery is separate.
"""
import argparse
import json
import logging
import os
from pathlib import Path
import secrets

import psycopg
from psycopg import sql
from dotenv import dotenv_values
from sqlalchemy import text

from backend.encryption import windows_protect
from backend.hosted_connections import PROJECT, POOLER, LOGIN_ROLES, create_hosted_transactions

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / '.runtime' / 'hosted-logins.dpapi'
CA = ROOT / 'prod-ca-2021.crt'


def load_bundle(create=False):
    if os.name != 'nt':
        raise RuntimeError('This local credential workflow requires Windows.')
    if not BUNDLE.exists() and create:
        payload = {'project': PROJECT, 'passwords': {cap: secrets.token_urlsafe(36) for cap in LOGIN_ROLES}}
        encrypted = windows_protect(json.dumps(payload).encode())
        BUNDLE.parent.mkdir(exist_ok=True)
        with BUNDLE.open('xb') as target:
            target.write(encrypted)
            target.flush()
            os.fsync(target.fileno())
    payload = json.loads(windows_protect(BUNDLE.read_bytes(), decrypt=True))
    if payload.get('project') != PROJECT or set(payload.get('passwords', {})) != set(LOGIN_ROLES):
        raise RuntimeError('Unexpected credential bundle target.')
    return payload['passwords']


def activate(passwords):
    logging.getLogger('dotenv.main').disabled = True
    password = dotenv_values(ROOT / '.env.supabase.admin', interpolate=False).get('LEXVIGIL_ADMIN_DATABASE_PASSWORD')
    if not password:
        raise RuntimeError('Administrative password is not configured locally.')
    with psycopg.connect(host=POOLER, port=5432, dbname='postgres',
            user='postgres.' + PROJECT, password=password, sslmode='verify-full',
            sslrootcert=str(CA), connect_timeout=10,
            options='-c statement_timeout=10000') as con:
        for cap, login in LOGIN_ROLES.items():
            row = con.execute('SELECT rolcanlogin,rolsuper,rolbypassrls,rolcreaterole,rolcreatedb,rolreplication FROM pg_roles WHERE rolname=%s', (login,)).fetchone()
            if row is None or any(row[1:]):
                raise RuntimeError('Missing or unsafe runtime role.')
            if row[0]:
                continue  # Never rotate a live credential implicitly.
            verifier = con.pgconn.encrypt_password(passwords[cap].encode(), login.encode(), b'scram-sha-256').decode()
            con.execute(sql.SQL('ALTER ROLE {} LOGIN PASSWORD {}').format(sql.Identifier(login), sql.Literal(verifier)))
    print(json.dumps({'activation': 'complete', 'passwords_displayed': False}))


def verify(passwords):
    db = create_hosted_transactions(passwords, CA)
    try:
        for cap, engine in db.engines.items():
            owner = 'supabase:00000000-0000-4000-8000-000000000001' if cap == 'tenant' else None
            for attempt in range(2):
                with db.transaction(cap, owner) as con:
                    role = con.execute(text('SELECT current_user')).scalar_one()
                    if role != 'lexvigil_' + cap:
                        raise RuntimeError('Unexpected effective database role.')
                with engine.begin() as con:
                    login, context = con.execute(text("SELECT current_user, nullif(current_setting('lexvigil.owner',true),'')")).one()
                    if login != LOGIN_ROLES[cap] or context is not None:
                        raise RuntimeError('Role or account context leaked across transactions.')
            print(json.dumps({'capability': cap, 'authenticated': True, 'role_checks': True, 'context_reset': True}))
    finally:
        for engine in db.engines.values():
            engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--activate', action='store_true', help='Create encrypted local secrets and activate only inactive runtime logins.')
    args = parser.parse_args()
    try:
        passwords = load_bundle(create=args.activate)
        if args.activate:
            activate(passwords)
        verify(passwords)
    except Exception as exc:
        # Driver exceptions may include DSNs or SQL. Never print their message.
        print(json.dumps({'status': 'failed', 'error_type': type(exc).__name__, 'sqlstate': getattr(exc, 'sqlstate', None)}))
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
