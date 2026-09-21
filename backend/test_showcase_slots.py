from contextlib import contextmanager
from unittest.mock import Mock
import asyncio
import pytest
from backend.showcase_slots import ShowcaseSlots, PURPOSE
from backend.hosted_reports import ShowcaseCapacityExceeded


def database(count=0):
    db, con = Mock(), Mock()
    con.execute.return_value.scalar_one.return_value = count
    @contextmanager
    def transaction(capability):
        assert capability == 'auth'
        yield con
    db.transaction = transaction
    return db, con


def test_acquire_serializes_and_inserts_no_document_or_owner():
    db, con = database(3)
    token = ShowcaseSlots(db).acquire()
    assert len(token) == 64
    calls = con.execute.call_args_list
    assert 'pg_advisory_xact_lock' in str(calls[0].args[0])
    assert calls[-1].args[1] == {'token': token, 'purpose': PURPOSE, 'ttl': 120}
    assert 'analyses' not in ' '.join(str(c.args[0]) for c in calls)


def test_full_slots_never_insert():
    db, con = database(4)
    with pytest.raises(ShowcaseCapacityExceeded):
        ShowcaseSlots(db).acquire()
    assert not any('INSERT' in str(c.args[0]) for c in con.execute.call_args_list)


@pytest.mark.parametrize('error', [ValueError('synthetic'), asyncio.CancelledError()])
def test_release_after_failure_or_cancellation(error):
    slots = ShowcaseSlots(Mock())
    slots.acquire = Mock(return_value='synthetic-token')
    slots.release = Mock()
    with pytest.raises(type(error)):
        with slots.hold():
            slots.release.assert_not_called()
            raise error
    slots.release.assert_called_once_with('synthetic-token')


def test_release_error_does_not_mask_success():
    slots = ShowcaseSlots(Mock())
    slots.acquire = Mock(return_value='synthetic-token')
    slots.release = Mock(side_effect=RuntimeError('private DSN must not be logged'))
    with slots.hold():
        pass


def test_release_scopes_token_and_purpose():
    db, con = database()
    ShowcaseSlots(db).release('synthetic-token')
    assert con.execute.call_args.args[1] == {'token':'synthetic-token', 'purpose':PURPOSE}
