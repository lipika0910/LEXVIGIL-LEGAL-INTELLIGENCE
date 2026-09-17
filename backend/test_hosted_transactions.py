from contextlib import contextmanager
from types import SimpleNamespace
import pytest
from backend.hosted_transactions import HostedTransactions, canonical_owner

OWNER = 'supabase:00000000-0000-4000-8000-000000000001'


class Engine:
    dialect = SimpleNamespace(name='postgresql')

    def __init__(self, capability):
        self.record = dict(rolcanlogin=True, unchanged=True, rolsuper=False,
                           rolbypassrls=False, rolcreaterole=False, rolcreatedb=False,
                           rolreplication=False, administrator=False,
                           tenant=capability == 'tenant', auth=capability == 'auth',
                           worker=capability == 'worker')
        self.calls = []
        self.commits = self.rollbacks = 0

    @contextmanager
    def begin(self):
        try:
            yield self
        except Exception:
            self.rollbacks += 1
            raise
        else:
            self.commits += 1

    def execute(self, query, params=None):
        self.calls.append((str(query), params))
        return self

    def mappings(self):
        return self

    def one(self):
        return self.record


def setup():
    engines = {key: Engine(key) for key in ('tenant', 'auth', 'worker')}
    return HostedTransactions(engines), engines


@pytest.mark.parametrize('owner', [None, '', 'local:1', 'supabase:bad',
                                  OWNER + "'; RESET ROLE; --", OWNER.upper()])
def test_bad_identity_rejected_before_connection(owner):
    db, engines = setup()
    with pytest.raises(ValueError):
        with db.transaction('tenant', owner):
            pytest.fail('Invalid identity reached transaction body')
    assert engines['tenant'].calls == []


def test_tenant_identity_bound_each_transaction():
    db, engines = setup()
    for owner in (OWNER, OWNER[:-1] + '2'):
        with db.transaction('tenant', owner) as connection:
            assert connection.calls[-1][1] == {'owner': owner}
            assert 'true)' in connection.calls[-1][0]
    assert engines['tenant'].commits == 2
    assert sum('SET LOCAL ROLE' in q for q, _ in engines['tenant'].calls) == 2


@pytest.mark.parametrize('field,value', [
    ('rolcanlogin', False), ('unchanged', False), ('rolsuper', True),
    ('rolbypassrls', True), ('rolcreaterole', True), ('rolcreatedb', True),
    ('rolreplication', True), ('administrator', True), ('auth', True),
    ('worker', True), ('tenant', False),
])
def test_unsafe_login_rejected_before_role_or_identity_set(field, value):
    db, engines = setup()
    engines['tenant'].record[field] = value
    with pytest.raises(RuntimeError, match='Unsafe database credential'):
        with db.transaction('tenant', OWNER):
            pytest.fail('Unsafe connection reached body')
    assert len(engines['tenant'].calls) == 1
    assert engines['tenant'].rollbacks == 1


@pytest.mark.parametrize('capability', ['auth', 'worker'])
def test_non_tenant_clears_identity_and_rejects_owner(capability):
    db, engines = setup()
    with pytest.raises(ValueError):
        with db.transaction(capability, OWNER):
            pass
    with db.transaction(capability) as connection:
        assert connection.calls[-1][1] == {'owner': ''}


def test_body_error_rolls_back():
    db, engines = setup()
    with pytest.raises(ValueError):
        with db.transaction('tenant', OWNER):
            raise ValueError('Synthetic failure')
    assert engines['tenant'].rollbacks == 1
    assert engines['tenant'].commits == 0


def test_unknown_capability_and_shared_pool_rejected():
    db, engines = setup()
    with pytest.raises(ValueError):
        with db.transaction('postgres', OWNER):
            pass
    engines['worker'] = engines['tenant']
    with pytest.raises(ValueError):
        HostedTransactions(engines)


def test_canonical_owner():
    assert canonical_owner(OWNER) == OWNER
