import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
import time
import json
import subprocess
import sys
import pytest
from sqlalchemy import create_engine,text
from backend.durable_jobs import DurableJobs,MAX_ATTEMPTS
from backend.originals import OriginalStore
from backend.encryption import OriginalCipher

@pytest.fixture
def setup_queue(tmp_path):
    db=create_engine('sqlite:///'+str(tmp_path/'queue.db'),connect_args={'check_same_thread':False})
    with db.begin() as con:
        con.execute(text('CREATE TABLE analyses (id TEXT PRIMARY KEY,owner TEXT,status TEXT,saved INTEGER,expires DOUBLE,result TEXT,error TEXT)'))
    store=OriginalStore(db,OriginalCipher(os.urandom(32)))
    queue=DurableJobs(db,store)
    def add(aid='a'):
        with db.begin() as con:
            con.execute(text("INSERT INTO analyses VALUES (:id,'owner','queued',0,:expires,NULL,NULL)"),{'id':aid,'expires':time.time()+86400})
        store.put(aid,'owner','contract.txt',b'1.1 Services\nThe supplier shall provide services.')
        queue.enqueue(aid,'owner','2026-09-15','')
    yield db,store,queue,add
    db.dispose()

def test_competing_workers_claim_once(setup_queue):
    db,store,queue,add=setup_queue; add()
    with ThreadPoolExecutor(max_workers=8) as workers:
        claims=list(workers.map(lambda _:queue.claim(),range(8)))
    assert sum(c is not None for c in claims)==1
    assert queue.status('a','other')=={'durable':False}

def test_expired_claim_is_recovered_and_old_result_is_fenced(setup_queue):
    db,store,queue,add=setup_queue; add(); first=queue.claim()
    with db.begin() as con: con.execute(text('UPDATE contract_jobs SET lease_until=0'))
    reopened=DurableJobs(db,store); second=reopened.claim()
    assert first['lease_token']!=second['lease_token'] and second['attempts']==2
    assert not queue.renew(first)
    assert not queue.finish(first,{'stale':True})
    assert reopened.finish(second,{'current':True})
    assert not reopened.finish(second,{'duplicate':True})
    with db.connect() as con: assert con.execute(text('SELECT result FROM analyses')).scalar()=='{"current": true}'

@pytest.mark.parametrize('action',['delete_original','delete_report','expire_original','expire_report'])
def test_deletion_and_expiry_block_late_publication(setup_queue,action):
    db,store,queue,add=setup_queue; add(); claim=queue.claim()
    sql={'delete_original':'DELETE FROM originals','delete_report':'DELETE FROM analyses','expire_original':'UPDATE originals SET expires=0','expire_report':'UPDATE analyses SET expires=0'}[action]
    with db.begin() as con: con.execute(text(sql))
    assert not queue.finish(claim,{'late':True})
    with db.connect() as con:
        assert con.execute(text("SELECT count(*) FROM analyses WHERE status='completed'")).scalar()==0

def test_repeated_worker_loss_has_bounded_attempts(setup_queue):
    db,store,queue,add=setup_queue; add()
    for _ in range(MAX_ATTEMPTS):
        assert queue.claim()
        with db.begin() as con: con.execute(text('UPDATE contract_jobs SET lease_until=0'))
    assert queue.claim() is None
    assert queue.status('a','owner')['state']=='failed'


def test_process_exit_recovers_after_real_lease_expiry(setup_queue):
    db,store,queue,add=setup_queue; add()
    with db.connect() as con:
        expiry=con.execute(text('SELECT expires FROM originals')).scalar()
    # Crash only a synthetic test claimant. No application process or user data is touched.
    program='''
import json, os, sys
from types import SimpleNamespace
from sqlalchemy import create_engine
import backend.durable_jobs as jobs
jobs.LEASE_SECONDS=1
db=create_engine(sys.argv[1])
claim=jobs.DurableJobs(db,SimpleNamespace(enabled=True)).claim()
print(json.dumps(claim),flush=True)
os._exit(23)
'''
    child=subprocess.run([sys.executable,'-c',program,str(db.url)],capture_output=True,text=True,timeout=15)
    assert child.returncode==23,child.stderr
    abandoned=json.loads(child.stdout)
    assert queue.claim() is None
    time.sleep(1.1)
    recovered=DurableJobs(db,store).claim()
    assert recovered and recovered['attempts']==2
    assert not queue.finish(abandoned,{'stale':True})
    assert queue.finish(recovered,asyncio.run(queue.execute(recovered)))
    with db.connect() as con:
        assert con.execute(text('SELECT expires FROM originals')).scalar()==expiry
        assert con.execute(text("SELECT count(*) FROM analyses WHERE status='completed'")).scalar()==1

def test_reopened_queue_completes_without_extending_original(setup_queue):
    db,store,queue,add=setup_queue; add()
    with db.connect() as con: expiry=con.execute(text('SELECT expires FROM originals')).scalar()
    reopened=DurableJobs(db,store)
    async def run():
        worker=asyncio.create_task(reopened.worker())
        try:
            for _ in range(250):
                if reopened.status('a','owner')['state']=='done': return
                await asyncio.sleep(.02)
            pytest.fail('Worker did not complete')
        finally:
            worker.cancel()
            try: await worker
            except asyncio.CancelledError: pass
    asyncio.run(run())
    with db.connect() as con:
        assert con.execute(text('SELECT expires FROM originals')).scalar()==expiry
        assert con.execute(text('SELECT status FROM analyses')).scalar()=='completed'


@pytest.mark.parametrize('action',['delete_original','delete_report','expire_original','expire_report','replace_lease'])
def test_retention_or_lease_loss_stops_active_process(setup_queue,tmp_path,monkeypatch,action):
    from backend.test_isolated_processing import TREE_PROGRAM,alive
    from backend.isolated_processing import _run,ClaimLost
    db,store,queue,add=setup_queue; add(); claim=queue.claim()
    marker=tmp_path/'active-pids.json'
    async def slow_contract(data,name,language,as_of,keep_alive):
        return await _run([sys.executable,'-c',TREE_PROGRAM,str(marker)],b'go',keep_alive,heartbeat=.05,timeout=10)
    monkeypatch.setattr('backend.durable_jobs.run_contract',slow_contract)
    async def run():
        task=asyncio.create_task(queue.execute(claim))
        try:
            for _ in range(100):
                if marker.exists(): break
                await asyncio.sleep(.02)
            assert marker.exists()
            pids=json.loads(marker.read_text())
            sql={'delete_original':'DELETE FROM originals','delete_report':'DELETE FROM analyses',
                 'expire_original':'UPDATE originals SET expires=0','expire_report':'UPDATE analyses SET expires=0',
                 'replace_lease':"UPDATE contract_jobs SET lease_token='replacement'"}[action]
            with db.begin() as con: con.execute(text(sql))
            with pytest.raises(ClaimLost): await asyncio.wait_for(task,5)
            # Windows schedules descendant termination asynchronously after
            # closing the job handle, even once the direct child is reaped.
            for _ in range(100):
                if not any(alive(pid) for pid in pids): break
                await asyncio.sleep(.02)
            assert not any(alive(pid) for pid in pids)
            assert not queue.finish(claim,{'late':True})
        finally:
            if not task.done(): task.cancel()
            await asyncio.gather(task,return_exceptions=True)
    asyncio.run(run())


def test_repeated_worker_shutdown_does_not_swallow_cancellation(setup_queue):
    db,store,queue,add=setup_queue
    async def run():
        for iteration in range(10):
            aid=str(iteration); add(aid)
            worker=asyncio.create_task(queue.worker())
            try:
                for _ in range(250):
                    if queue.status(aid,'owner')['state']=='done': break
                    await asyncio.sleep(.02)
                assert queue.status(aid,'owner')['state']=='done'
            finally:
                worker.cancel()
                with pytest.raises(asyncio.CancelledError):
                    await asyncio.wait_for(worker,2)
    asyncio.run(run())
