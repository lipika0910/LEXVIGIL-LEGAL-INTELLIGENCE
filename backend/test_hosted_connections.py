from pathlib import Path
from types import SimpleNamespace

import pytest

from backend.hosted_connections import create_hosted_transactions, LOGIN_ROLES, PROJECT, POOLER

CA = Path(__file__).resolve().parents[1] / 'prod-ca-2021.crt'
PASSWORDS = {cap: cap + '-synthetic-test-password-123456' for cap in LOGIN_ROLES}


class Engine:
    dialect = SimpleNamespace(name='postgresql')
    disposed = False

    def dispose(self):
        self.disposed = True


def test_verified_separate_bounded_pools():
    calls = []

    def factory(url, **kwargs):
        calls.append((url, kwargs))
        return Engine()

    db = create_hosted_transactions(PASSWORDS, CA, engine_factory=factory)
    assert len({id(e) for e in db.engines.values()}) == 3
    for cap, (url, options) in zip(LOGIN_ROLES, calls):
        assert url.username == LOGIN_ROLES[cap] + '.' + PROJECT
        assert url.host == POOLER and url.port == 5432
        assert url.password == PASSWORDS[cap]
        assert options['connect_args']['sslmode'] == 'verify-full'
        assert Path(options['connect_args']['sslrootcert']) == CA
        assert options['connect_args']['connect_timeout'] == 10
        assert options['pool_size'] == 1 and options['max_overflow'] == 0
        assert options['hide_parameters'] and not options['echo']


@pytest.mark.parametrize('passwords', [None, {}, {'tenant': 'x'},
    dict.fromkeys(LOGIN_ROLES, 'same-password-for-everyone-123456'),
    {**PASSWORDS, 'worker': 'short'}, {**PASSWORDS, 'auth': None},
    {**PASSWORDS, 'auth': 'x' * 30 + '\x00'}])
def test_invalid_secrets_never_construct_pools(passwords):
    with pytest.raises(ValueError):
        create_hosted_transactions(passwords, CA,
            engine_factory=lambda *a, **k: pytest.fail('Factory must not run'))


def test_invalid_certificate_rejected(tmp_path):
    with pytest.raises(ValueError, match='CA file'):
        create_hosted_transactions(PASSWORDS, tmp_path / 'missing.crt')


def test_partial_construction_disposes_pools_and_redacts_errors():
    engine = Engine()
    calls = 0

    def factory(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise ValueError(PASSWORDS['auth'])
        return engine

    with pytest.raises(RuntimeError) as exc:
        create_hosted_transactions(PASSWORDS, CA, engine_factory=factory)
    assert engine.disposed
    assert str(exc.value) == 'Hosted connection setup failed.'
