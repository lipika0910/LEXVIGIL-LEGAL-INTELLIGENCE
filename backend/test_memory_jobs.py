import asyncio
import json
import sys
import time
from sqlalchemy import text
from backend.memory_jobs import MemoryJobs
from backend.test_durable_jobs import setup_queue
from backend.test_isolated_processing import TREE_PROGRAM, alive
from backend.isolated_processing import _run


def insert(db, aid):
    with db.begin() as con:
        con.execute(text("INSERT INTO analyses VALUES (:id,'owner','queued',0,:expiry,NULL,NULL)"),
                    {'id': aid, 'expiry': time.time() + 86400})


def test_memory_queue_bounds_concurrency_and_shutdown(setup_queue, monkeypatch):
    db, _, _, _ = setup_queue
    started = []
    async def slow(data, name, *args):
        started.append(name)
        await asyncio.Event().wait()
    monkeypatch.setattr('backend.memory_jobs.run_contract', slow)
    async def run():
        jobs = MemoryJobs(db)
        for i in range(3):
            insert(db, str(i))
            jobs.submit(str(i), 'owner', b'not stored', str(i), '', None)
        for _ in range(100):
            if len(started) == 2:
                break
            await asyncio.sleep(.02)
        assert len(started) == 2
        await asyncio.wait_for(jobs.close(), 3)
        assert not jobs.tasks
    asyncio.run(run())
    with db.connect() as con:
        assert con.execute(text("SELECT count(*) FROM analyses WHERE status='failed'")).scalar() == 3
        assert con.execute(text('SELECT count(*) FROM originals')).scalar() == 0
        assert con.execute(text('SELECT count(*) FROM contract_jobs')).scalar() == 0


def test_memory_shutdown_stops_real_process_tree(setup_queue, tmp_path, monkeypatch):
    db, _, _, _ = setup_queue
    marker = tmp_path / 'memory-pids.json'
    insert(db, 'memory')
    async def slow(data, name, language, as_of, keep_alive):
        return await _run([sys.executable, '-c', TREE_PROGRAM, str(marker)], b'go', keep_alive, heartbeat=.05)
    monkeypatch.setattr('backend.memory_jobs.run_contract', slow)
    async def run():
        jobs = MemoryJobs(db)
        jobs.submit('memory', 'owner', b'not stored', 'memory.txt', '', None)
        try:
            for _ in range(100):
                if marker.exists():
                    break
                await asyncio.sleep(.02)
            assert marker.exists()
            pids = json.loads(marker.read_text())
            await asyncio.wait_for(jobs.close(), 5)
            for _ in range(100):
                if not any(alive(pid) for pid in pids):
                    break
                await asyncio.sleep(.02)
            assert not any(alive(pid) for pid in pids)
        finally:
            await jobs.close()
    asyncio.run(run())
    with db.connect() as con:
        assert con.execute(text('SELECT status FROM analyses')).scalar() == 'failed'
        assert con.execute(text('SELECT count(*) FROM originals')).scalar() == 0


def test_memory_result_cannot_restore_deleted_or_expired_report(setup_queue):
    db, _, _, _ = setup_queue
    jobs = MemoryJobs(db)
    insert(db, 'expired')
    insert(db, 'deleted')
    with db.begin() as con:
        con.execute(text("UPDATE analyses SET expires=0 WHERE id='expired'"))
        con.execute(text("DELETE FROM analyses WHERE id='deleted'"))
    for aid in ('expired', 'deleted'):
        assert not jobs.current(aid, 'owner', True)
        jobs.finish(aid, 'owner', {'late': True})
    with db.connect() as con:
        assert con.execute(text("SELECT count(*) FROM analyses WHERE status='completed'")).scalar() == 0
