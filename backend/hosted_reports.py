"""Private hosted report persistence; API admission/processing is separate."""
import json
import secrets
from sqlalchemy import text
from backend.hosted_transactions import canonical_owner


class ReportUnavailable(LookupError):
    pass


class ShowcaseCapacityExceeded(RuntimeError):
    pass


class HostedReports:
    def __init__(self, transactions):
        self.db = transactions

    def reserve(self, owner, title):
        """Serialize admission across instances before starting expensive work.

        Count physical rows, including expired rows, so missing cleanup cannot
        silently exceed the storage budget. Abandoned queued rows fail closed
        and remain manually deletable by their owner.
        """
        canonical_owner(owner)
        with self.db.transaction('worker') as con:
            con.execute(text("SELECT pg_advisory_xact_lock(hashtextextended('lexvigil-showcase-admission',0))"))
            row = con.execute(text('''SELECT count(*) AS total,
                count(*) FILTER (WHERE owner=:owner) AS owned,
                count(*) FILTER (WHERE status IN ('queued','processing')) AS active
                FROM lexvigil_private.analyses'''), {'owner': owner}).mappings().one()
            if row['total'] >= 100 or row['owned'] >= 10:
                raise ShowcaseCapacityExceeded('Report capacity reached. Delete an existing report before retrying.')
            if row['active'] >= 4:
                raise ShowcaseCapacityExceeded('All showcase processing slots are occupied. Please try again later.')
            # The tenant insert commits before releasing the worker's global
            # admission lock. No request holds this lock during processing.
            return self.create(owner, title)

    def create(self, owner, title):
        if not isinstance(title, str) or not title.strip() or len(title) > 200:
            raise ValueError('A report title of 1–200 characters is required.')
        aid = secrets.token_hex(16)
        with self.db.transaction('tenant', owner) as con:
            con.execute(text('''INSERT INTO lexvigil_private.analyses
                (id,owner,status,title,kind,created,expires)
                VALUES (:id,:owner,'queued',:title,'contract',
                extract(epoch FROM statement_timestamp()),
                extract(epoch FROM statement_timestamp())+86400)'''),
                {'id': aid, 'owner': owner, 'title': title})
        return aid

    def get(self, owner, aid):
        with self.db.transaction('tenant', owner) as con:
            row = con.execute(text('''SELECT id,title,kind,status,saved,created,expires,error,result
                FROM lexvigil_private.analyses WHERE id=:id'''), {'id': aid}).mappings().first()
        if row is None:
            raise ReportUnavailable('Analysis not found or expired.')
        result = dict(row)
        result['result'] = json.loads(result['result']) if result['result'] else None
        return result

    def list(self, owner):
        with self.db.transaction('tenant', owner) as con:
            return [dict(row) for row in con.execute(text('''
                SELECT id,title,kind,status,saved,created,expires
                FROM lexvigil_private.analyses ORDER BY created DESC,id DESC LIMIT 100
            ''')).mappings()]

    def save(self, owner, aid):
        with self.db.transaction('tenant', owner) as con:
            row = con.execute(text('''UPDATE lexvigil_private.analyses SET saved=1
                WHERE id=:id AND status='completed' RETURNING id'''), {'id': aid}).first()
        if row is None:
            raise ReportUnavailable('Completed analysis not found or expired.')

    def delete(self, owner, aid):
        with self.db.transaction('tenant', owner) as con:
            row = con.execute(text('DELETE FROM lexvigil_private.analyses WHERE id=:id RETURNING id'), {'id': aid}).first()
        if row is None:
            raise ReportUnavailable('Analysis not found or expired.')

    def complete(self, owner, aid, report):
        canonical_owner(owner)
        if not isinstance(report, dict) or report.get('kind') != 'contract':
            raise ValueError('Only contract reports are accepted.')
        payload = json.dumps(report, ensure_ascii=False, allow_nan=False)
        if len(payload.encode()) > 2 * 1024 * 1024:
            raise ValueError('Report exceeds the showcase storage limit.')
        with self.db.transaction('worker') as con:
            row = con.execute(text('''UPDATE lexvigil_private.analyses
                SET status='completed',result=:result,error=NULL
                WHERE id=:id AND owner=:owner AND status IN ('queued','processing')
                AND expires>extract(epoch FROM statement_timestamp()) RETURNING id'''),
                {'id': aid, 'owner': owner, 'result': payload}).first()
        # A deleted, expired, or already published report cannot be resurrected.
        return row is not None
