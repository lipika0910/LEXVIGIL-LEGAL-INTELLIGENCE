"""Read-only hosted bootstrap probe; credentials never leave this process."""
import json
from pathlib import Path
from dotenv import dotenv_values
from fastapi.testclient import TestClient
from sqlalchemy import text
from backend.showcase_bootstrap import build_showcase_app
from backend.hosted_connections import create_hosted_transactions
from scripts.provision_hosted_logins import load_bundle


def main():
    root=Path(__file__).resolve().parent.parent
    dev=dotenv_values(root/'.env.supabase.development',interpolate=False)
    env={'LEXVIGIL_RELEASE_PROFILE':'showcase',
         'SUPABASE_URL':dev.get('SUPABASE_URL',''),
         'SUPABASE_PUBLISHABLE_KEY':dev.get('SUPABASE_PUBLISHABLE_KEY',''),
         'APP_ORIGIN':'https://bootstrap-check.example',
         'VERCEL':'1','VERCEL_REGION':'bom1'}
    for cap,password in load_bundle().items():
        env['LEXVIGIL_DB_'+cap.upper()+'_PASSWORD']=password
    created=[]
    def factory(*args):
        db=create_hosted_transactions(*args); created.append(db); return db
    try:
        app=build_showcase_app(env,transactions_factory=factory)
        for cap in ('tenant','auth','worker'):
            owner='supabase:00000000-0000-4000-8000-000000000001' if cap=='tenant' else None
            with created[0].transaction(cap,owner) as con:
                assert con.execute(text('SELECT 1')).scalar_one()==1
        with TestClient(app,base_url=env['APP_ORIGIN']) as client:
            assert client.get('/api/health').json()['release_scope']['profile']=='showcase'
            assert client.get('/api/auth/options').json()['managed'] is True
            assert client.get('/api/me').status_code==401
        print(json.dumps({'bootstrap':'passed','restricted_connections':3,
                          'auth_options':'managed','anonymous_workspace':'denied',
                          'runtime':'local Windows, not deployed Linux'}))
    finally:
        for db in created:
            for engine in db.engines.values(): engine.dispose()


if __name__=='__main__':
    try: main()
    except Exception as exc:
        print(json.dumps({'status':'failed','error_type':type(exc).__name__}))
        raise SystemExit(1) from None
