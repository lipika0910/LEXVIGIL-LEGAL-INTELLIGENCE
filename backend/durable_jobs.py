"""SQLite development queue: leased claims and fenced, retention-aware publication."""
import asyncio
import json
import logging
import secrets
import time
from sqlalchemy import text
from .isolated_processing import run_contract, ClaimLost

LEASE_SECONDS=30
MAX_ATTEMPTS=3

class DurableJobs:
    def __init__(self,db,originals):
        self.db,self.originals=db,originals
        self.enabled=originals.enabled
        if not self.enabled: return
        with db.begin() as con:
            con.execute(text('CREATE TABLE IF NOT EXISTS contract_jobs (id TEXT PRIMARY KEY, owner TEXT NOT NULL, as_of TEXT NOT NULL, ocr_language TEXT NOT NULL, state TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0, lease_token TEXT, lease_until DOUBLE PRECISION NOT NULL DEFAULT 0)'))
            con.execute(text('CREATE INDEX IF NOT EXISTS contract_jobs_claim_idx ON contract_jobs(state,lease_until)'))

    def enqueue(self,aid,uid,as_of,language):
        with self.db.begin() as con:
            con.execute(text("INSERT INTO contract_jobs(id,owner,as_of,ocr_language,state) SELECT :id,:owner,:as_of,:language,'queued' WHERE EXISTS (SELECT 1 FROM originals WHERE analysis_id=:id AND owner=:owner AND expires>:now)"),{'id':aid,'owner':uid,'as_of':as_of,'language':language,'now':time.time()})
            if not con.execute(text('SELECT id FROM contract_jobs WHERE id=:id'),{'id':aid}).scalar():
                raise ValueError('Original unavailable for durable processing.')

    def sweep(self,con):
        if not self.enabled: return
        con.execute(text('DELETE FROM contract_jobs WHERE NOT EXISTS (SELECT 1 FROM analyses WHERE analyses.id=contract_jobs.id AND analyses.owner=contract_jobs.owner)'))
        invalid=con.execute(text("SELECT j.id FROM contract_jobs j WHERE j.state IN ('queued','running') AND (NOT EXISTS (SELECT 1 FROM originals o WHERE o.analysis_id=j.id AND o.owner=j.owner AND o.expires>:now) OR NOT EXISTS (SELECT 1 FROM analyses a WHERE a.id=j.id AND a.owner=j.owner AND (a.saved=1 OR a.expires>:now)))"),{'now':time.time()}).scalars().all()
        for aid in invalid:
            con.execute(text("UPDATE analyses SET status='failed',error='The original was deleted or expired before processing completed. Please upload again.' WHERE id=:id AND status IN ('queued','processing')"),{'id':aid})
            con.execute(text("UPDATE contract_jobs SET state='cancelled',lease_token=NULL,lease_until=0 WHERE id=:id"),{'id':aid})

    def claim(self):
        if not self.enabled: return None
        now=time.time()
        with self.db.begin() as con:
            con.exec_driver_sql('BEGIN IMMEDIATE')
            self.sweep(con)
            exhausted=con.execute(text("SELECT id FROM contract_jobs WHERE state='running' AND lease_until<=:now AND attempts>=:max"),{'now':now,'max':MAX_ATTEMPTS}).scalars().all()
            for aid in exhausted:
                con.execute(text("UPDATE contract_jobs SET state='failed',lease_token=NULL WHERE id=:id"),{'id':aid})
                con.execute(text("UPDATE analyses SET status='failed',error='Processing stopped repeatedly. Please resubmit or contact support.' WHERE id=:id AND status IN ('queued','processing')"),{'id':aid})
            row=con.execute(text("SELECT * FROM contract_jobs WHERE (state='queued' OR (state='running' AND lease_until<=:now)) AND attempts<:max ORDER BY rowid LIMIT 1"),{'now':now,'max':MAX_ATTEMPTS}).mappings().first()
            if not row: return None
            job=dict(row); job['lease_token']=secrets.token_hex(24); job['attempts']+=1
            con.execute(text("UPDATE contract_jobs SET state='running',attempts=:attempts,lease_token=:lease_token,lease_until=:until WHERE id=:id"),{**job,'until':now+LEASE_SECONDS})
            con.execute(text("UPDATE analyses SET status='processing',error=NULL WHERE id=:id AND owner=:owner"),job)
            return job

    def renew(self,job):
        with self.db.begin() as con:
            con.exec_driver_sql('BEGIN IMMEDIATE')
            self.sweep(con)
            result=con.execute(text("UPDATE contract_jobs SET lease_until=:until WHERE id=:id AND lease_token=:lease_token AND state='running' AND lease_until>:now"),{**job,'now':time.time(),'until':time.time()+LEASE_SECONDS})
            return result.rowcount==1

    def finish(self,job,result=None,error=None):
        with self.db.begin() as con:
            con.exec_driver_sql('BEGIN IMMEDIATE')
            self.sweep(con)
            valid=con.execute(text("SELECT id FROM contract_jobs WHERE id=:id AND owner=:owner AND state='running' AND lease_token=:lease_token AND lease_until>:now"),{**job,'now':time.time()}).scalar()
            if not valid: return False
            con.execute(text("UPDATE analyses SET status=:status,result=:result,error=:error WHERE id=:id AND owner=:owner AND status='processing'"),{**job,'status':'failed' if error else 'completed','result':json.dumps(result) if result is not None else None,'error':error})
            con.execute(text('UPDATE contract_jobs SET state=:state,lease_token=NULL,lease_until=0 WHERE id=:id'),{'id':job['id'],'state':'failed' if error else 'done'})
            return True

    def load_input(self,job):
        with self.db.connect() as con:
            row=con.execute(text('SELECT payload,filename FROM originals WHERE analysis_id=:id AND owner=:owner AND expires>:now'),{**job,'now':time.time()}).first()
        if not row: raise ValueError('The original is unavailable. Please upload again.')
        data=self.originals.decrypt(row[0],job['id'],job['owner'])
        return data,row[1]

    async def execute(self,job):
        data,name=await asyncio.to_thread(self.load_input,job)
        async def keep_alive():
            return await asyncio.to_thread(self.renew,job)
        if not await keep_alive(): raise ClaimLost()
        return await run_contract(data,name,job['ocr_language'],job['as_of'] or None,keep_alive)

    async def worker(self):
        while True:
            try:
                job=await asyncio.to_thread(self.claim)
                if not job:
                    await asyncio.sleep(.25); continue
                try:
                    result=await self.execute(job)
                    await asyncio.to_thread(self.finish,job,result)
                except ClaimLost:
                    pass
                except ValueError as exc:
                    await asyncio.to_thread(self.finish,job,error=str(exc)[:300])
                except Exception:
                    logging.getLogger('lexvigil').error('Durable contract attempt failed')
                    await asyncio.to_thread(self.finish,job,error='Contract processing could not complete. Check the original and retry.')
            except asyncio.CancelledError: raise
            except Exception:
                logging.getLogger('lexvigil').error('Durable worker temporarily unavailable')
                await asyncio.sleep(2)

    def status(self,aid,uid):
        if not self.enabled: return {'durable':False}
        with self.db.connect() as con:
            row=con.execute(text('SELECT state,attempts FROM contract_jobs WHERE id=:id AND owner=:owner'),{'id':aid,'owner':uid}).mappings().first()
        return {'durable':bool(row),**(dict(row) if row else {})}
