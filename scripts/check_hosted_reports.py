"""Live synthetic two-account report check; cleanup only IDs created here."""
import json
from uuid import uuid4
from backend.hosted_connections import create_hosted_transactions
from backend.hosted_reports import HostedReports, ReportUnavailable
from scripts.provision_hosted_logins import load_bundle, CA


def main():
    db = create_hosted_transactions(load_bundle(), CA)
    reports = HostedReports(db)
    a, b = ('supabase:' + str(uuid4()) for _ in range(2))
    created = []
    try:
        aid = reports.create(a, 'Synthetic hosted isolation check')
        created.append((a, aid))
        bid = reports.create(b, 'Synthetic second-account check')
        created.append((b, bid))
        assert reports.get(a, aid)['status'] == 'queued'
        assert {r['id'] for r in reports.list(a)} == {aid}
        assert {r['id'] for r in reports.list(b)} == {bid}
        for operation in (reports.get, reports.save, reports.delete):
            try:
                operation(b, aid)
            except ReportUnavailable:
                pass
            else:
                raise AssertionError('Cross-account operation was accepted')
        assert not reports.complete(b, aid, {'kind': 'contract'})
        assert reports.complete(a, aid, {'kind': 'contract', 'title': 'Synthetic', 'findings': []})
        assert not reports.complete(a, aid, {'kind': 'contract'})
        reports.save(a, aid)
        assert reports.get(a, aid)['saved'] == 1
        reports.delete(a, aid)
        created.remove((a, aid))
        assert not reports.complete(a, aid, {'kind': 'contract'})
        print(json.dumps({'report_flow': 'passed', 'cross_account_denial': True,
                          'duplicate_completion_denied': True, 'deletion_resurrection_denied': True}))
    finally:
        try:
            for owner, aid in created:
                reports.delete(owner, aid)
        finally:
            for engine in db.engines.values():
                engine.dispose()


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(json.dumps({'status': 'failed', 'error_type': type(exc).__name__}))
        raise SystemExit(1) from None
