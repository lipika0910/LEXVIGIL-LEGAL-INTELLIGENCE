"""Short-lived compute leases independent of deletable report records.

Use the private auth-flow store's existing expiry/cleanup mechanism. No
document content or account identity is stored in these leases.
"""
import logging
import secrets
import time
from contextlib import contextmanager
from sqlalchemy import text
from .hosted_reports import ShowcaseCapacityExceeded

PURPOSE = 'showcase-processing-v1'
LEASE_SECONDS = 120
MAX_SLOTS = 4


class ShowcaseSlots:
    def __init__(self, transactions):
        self.db = transactions

    def acquire(self):
        token = secrets.token_hex(32)
        with self.db.transaction('auth') as con:
            con.execute(text('SELECT pg_advisory_xact_lock(hashtextextended(:key,0))'), {'key': PURPOSE})
            con.execute(text('''DELETE FROM lexvigil_private.auth_flows
                WHERE purpose=:purpose AND expires<=extract(epoch FROM clock_timestamp())'''), {'purpose': PURPOSE})
            count = con.execute(text('''SELECT count(*) FROM lexvigil_private.auth_flows
                WHERE purpose=:purpose'''), {'purpose': PURPOSE}).scalar_one()
            if count >= MAX_SLOTS:
                raise ShowcaseCapacityExceeded('All showcase processing slots are occupied. Please try again later.')
            con.execute(text('''INSERT INTO lexvigil_private.auth_flows(token,verifier,purpose,expires)
                VALUES (:token,'',:purpose,extract(epoch FROM clock_timestamp())+:ttl)'''),
                {'token': token, 'purpose': PURPOSE, 'ttl': LEASE_SECONDS})
        return token

    def release(self, token):
        with self.db.transaction('auth') as con:
            con.execute(text('''DELETE FROM lexvigil_private.auth_flows
                WHERE token=:token AND purpose=:purpose'''), {'token': token, 'purpose': PURPOSE})

    @contextmanager
    def hold(self):
        started = time.monotonic()
        token = self.acquire()
        try:
            # Refuse to start after a delayed acquisition; leave generous
            # headroom for the processor's independent 20-second deadline.
            if time.monotonic() - started > 30:
                raise ShowcaseCapacityExceeded('Processing admission timed out. Please retry.')
            yield
        finally:
            # Called only after the processor has returned/unwound its child
            # cleanup. A hard crash leaves the lease until expiry instead.
            try:
                self.release(token)
            except Exception:
                logging.getLogger(__name__).warning('Processing slot release failed; lease will expire.')
