import base64
import os
import pytest
from backend.configuration import production_errors, validate_environment


def valid():
    return {'LEXVIGIL_ENV': 'production', 'AUTH_PROVIDER': 'supabase',
            'APP_ORIGIN': 'https://lexvigil.example.com',
            'DATABASE_URL': 'postgresql+psycopg://app:synthetic-password@db.example.com/lexvigil?sslmode=verify-full',
            'SUPABASE_URL': 'https://separate-production.supabase.co',
            'SUPABASE_PUBLISHABLE_KEY': 'sb_publishable_synthetic',
            'ORIGINAL_ENCRYPTION_KEY': base64.b64encode(os.urandom(32)).decode()}


def test_development_unchanged_and_valid_production_shape():
    assert production_errors({}) == []
    assert production_errors(valid()) == []


@pytest.mark.parametrize('host', [
    {'VERCEL': '1'}, {'VERCEL_ENV': 'preview'}, {'VERCEL_ENV': 'production'},
])
@pytest.mark.parametrize('settings', [{}, {'LEXVIGIL_ENV': 'development'},
                                      {'LEXVIGIL_ENV': 'test'}, valid()])
def test_unsupported_vercel_runtime_fails_before_database_startup(host, settings):
    with pytest.raises(RuntimeError, match='cannot run on Vercel Functions'):
        validate_environment({**settings, **host})


def test_unhosted_local_environment_is_unchanged():
    validate_environment({})
    validate_environment({'LEXVIGIL_ENV': 'test'})
    validate_environment(valid())


@pytest.mark.parametrize('mode',['Production','production ','staging','unknown'])
def test_environment_typo_cannot_silently_disable_production_guards(mode):
    with pytest.raises(RuntimeError,match='LEXVIGIL_ENV'):
        validate_environment({'LEXVIGIL_ENV':mode})


@pytest.mark.parametrize('field,value', [
    ('AUTH_PROVIDER','local'), ('APP_ORIGIN','http://lexvigil.example.com'),
    ('APP_ORIGIN','https://localhost'), ('APP_ORIGIN','https://127.0.0.1'),
    ('APP_ORIGIN','https://lexvigil.example.com/path'), ('APP_ORIGIN','https://name:secret@lexvigil.example.com'),
    ('DATABASE_URL','sqlite:///production.db'),
    ('DATABASE_URL','postgresql+psycopg://app:secret@db.example.com/app?sslmode=require'),
    ('SUPABASE_URL','https://mbnwdfdxksiuptwonjev.supabase.co'),
    ('SUPABASE_URL','http://separate-production.supabase.co'),
    ('SUPABASE_PUBLISHABLE_KEY','sb_secret_sensitive'),
    ('ORIGINAL_ENCRYPTION_KEY',''), ('ORIGINAL_ENCRYPTION_KEY',base64.b64encode(bytes(32)).decode()),
    ('WEB_CONCURRENCY','4'),
])
def test_unsafe_production_configuration_is_rejected(field,value):
    env=valid(); env[field]=value
    assert production_errors(env)
    with pytest.raises(RuntimeError) as error: validate_environment(env)
    assert 'synthetic-password' not in str(error.value)
    assert 'sb_secret_sensitive' not in str(error.value)
