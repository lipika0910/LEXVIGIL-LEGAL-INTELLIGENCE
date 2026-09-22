"""Deliver selected preview environment via CLI stdin; never print values."""
import argparse
import json
import subprocess
from pathlib import Path
from dotenv import dotenv_values
from scripts.provision_hosted_logins import load_bundle

ROOT=Path(__file__).resolve().parent.parent
PROJECT='prj_R0tVgJx6m9mzO8Bbh19BErnAfoKv'
CLI=Path('C:/Users/rakes/AppData/Roaming/npm/node_modules/vercel/dist/index.js')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--approved-production',action='store_true',help='Use only after explicit user approval of production credential transfer.')
    production=parser.parse_args().approved_production
    linked=json.loads((ROOT/'.vercel/project.json').read_text())
    if linked['projectId']!=PROJECT or linked['orgId']!='team_wsjnqqTs5TSLGPjUACKId83W':
        raise RuntimeError('Unexpected Vercel target')
    cfg=dotenv_values(ROOT/'.env.supabase.development',interpolate=False)
    values={'LEXVIGIL_RELEASE_PROFILE':'showcase',
            'SUPABASE_URL':cfg['SUPABASE_URL'],
            'SUPABASE_PUBLISHABLE_KEY':cfg['SUPABASE_PUBLISHABLE_KEY'],
            'APP_ORIGIN':'https://lexvigil.vercel.app' if production else 'https://lexvigil-git-codex-showcase-preview-rakesh-projects.vercel.app'}
    if values['SUPABASE_URL']!='https://mbnwdfdxksiuptwonjev.supabase.co':
        raise RuntimeError('Unexpected Supabase target')
    for cap,password in load_bundle().items():
        values['LEXVIGIL_DB_'+cap.upper()+'_PASSWORD']=password
    for key,value in values.items():
        target=['production'] if production else ['preview','codex/showcase-preview']
        command=['node',str(CLI),'env','add',key,*target,'--yes',
                 '--scope','rakesh-projects']
        if key.endswith('_PASSWORD'): command.append('--sensitive')
        result=subprocess.run(command,input=value,text=True,capture_output=True,
            cwd=ROOT,timeout=90,creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode:
            raise RuntimeError('Environment upload failed for '+key)
        print(json.dumps({'configured':key,'target':'production' if production else 'preview/codex/showcase-preview'}),flush=True)


if __name__=='__main__':
    try: main()
    except Exception as exc:
        print(json.dumps({'status':'failed','error_type':type(exc).__name__}))
        raise SystemExit(1) from None
