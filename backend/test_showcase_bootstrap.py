from unittest.mock import Mock
import pytest
from backend.showcase_bootstrap import validate_environment, build_showcase_app


def environment():
    return {'LEXVIGIL_RELEASE_PROFILE':'showcase',
            'SUPABASE_URL':'https://mbnwdfdxksiuptwonjev.supabase.co',
            'APP_ORIGIN':'https://lexvigil.example',
            'SUPABASE_PUBLISHABLE_KEY':'sb_publishable_synthetic',
            'LEXVIGIL_DB_TENANT_PASSWORD':'t'*32,
            'LEXVIGIL_DB_AUTH_PASSWORD':'a'*32,
            'LEXVIGIL_DB_WORKER_PASSWORD':'w'*32,
            'VERCEL':'1','VERCEL_REGION':'bom1'}


@pytest.mark.parametrize('key,value',[
 ('LEXVIGIL_RELEASE_PROFILE','development'),('SUPABASE_URL','https://wrong.supabase.co'),
 ('APP_ORIGIN','http://localhost:5173'),('APP_ORIGIN','https://example.com/path'),
 ('APP_ORIGIN','https://user:pass@example.com'),('APP_ORIGIN','https://example.com:bad'),
 ('APP_ORIGIN','https://example.com:8443'),('APP_ORIGIN','https://example.com/'),
 ('VERCEL_REGION','iad1'),('VERCEL_REGION',''),
 ('SUPABASE_PUBLISHABLE_KEY','sb_secret_no'),('LEXVIGIL_DB_AUTH_PASSWORD','short'),
 ('LEXVIGIL_DB_AUTH_PASSWORD','t'*32)])
def test_rejects_unsafe_configuration_before_constructing_connections(key,value):
    env = environment(); env[key]=value
    factory=Mock()
    with pytest.raises(ValueError):
        build_showcase_app(env, transactions_factory=factory)
    factory.assert_not_called()


def test_builds_only_hosted_factory_and_passes_public_ca():
    tx, provider, app = Mock(), Mock(), Mock()
    factory=Mock(return_value=tx)
    provider_factory=Mock(return_value=provider)
    app_factory=Mock(return_value=app)
    result=build_showcase_app(environment(),transactions_factory=factory,
        provider_factory=provider_factory,app_factory=app_factory)
    assert result is app
    assert factory.call_args.args[1].name=='prod-ca-2021.crt'
    assert app_factory.call_args.args[:3]==(tx,provider,'https://lexvigil.example')


def test_disposes_pools_if_app_creation_fails():
    tx=Mock(); tx.engines={'auth':Mock(),'tenant':Mock(),'worker':Mock()}
    with pytest.raises(RuntimeError,match='Hosted application setup failed'):
        build_showcase_app(environment(),transactions_factory=Mock(return_value=tx),
            app_factory=Mock(side_effect=RuntimeError('private details')))
    for engine in tx.engines.values():
        engine.dispose.assert_called_once()
