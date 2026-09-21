from contextlib import contextmanager
from unittest.mock import Mock

import pytest

from backend.hosted_reports import HostedReports, ShowcaseCapacityExceeded

OWNER = 'supabase:00000000-0000-4000-8000-000000000001'


class Database:
    def __init__(self, total=0, owned=0, active=0):
        self.locked = False
        self.con = Mock()
        self.con.execute.return_value.mappings.return_value.one.return_value = {
            'total': total, 'owned': owned, 'active': active}

    @contextmanager
    def transaction(self, capability):
        assert capability == 'worker'
        self.locked = True
        try:
            yield self.con
        finally:
            self.locked = False


@pytest.mark.parametrize('counts', [dict(total=100), dict(owned=10), dict(active=4)])
def test_capacity_rejects_before_insert(counts):
    db = Database(**counts)
    reports = HostedReports(db)
    reports.create = Mock()
    with pytest.raises(ShowcaseCapacityExceeded):
        reports.reserve(OWNER, 'Synthetic')
    reports.create.assert_not_called()
    assert not db.locked


def test_reservation_commits_before_admission_lock_released():
    db = Database(total=99, owned=9, active=3)
    reports = HostedReports(db)

    def create(owner, title):
        assert db.locked
        assert owner == OWNER and title == 'Synthetic'
        return 'synthetic-id'

    reports.create = create
    assert reports.reserve(OWNER, 'Synthetic') == 'synthetic-id'
    assert not db.locked
    assert 'pg_advisory_xact_lock' in str(db.con.execute.call_args_list[0].args[0])


def test_invalid_identity_never_queries_capacity():
    db = Database()
    with pytest.raises(ValueError):
        HostedReports(db).reserve('unverified', 'Synthetic')
    db.con.execute.assert_not_called()
