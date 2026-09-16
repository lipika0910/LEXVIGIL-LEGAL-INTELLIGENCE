"""Lifecycle-scoped, non-persistent processing for non-consented uploads."""
import asyncio
import json
import logging
import time
from sqlalchemy import text
from .isolated_processing import run_contract, ClaimLost


class MemoryJobs:
    def __init__(self, db):
        self.db = db
        self.tasks = set()
        self.slots = asyncio.Semaphore(2)

    def submit(self, aid, uid, data, name, language, as_of):
        task = asyncio.create_task(self.process(aid, uid, data, name, language, as_of))
        self.tasks.add(task)
        task.add_done_callback(self.completed)

    def completed(self, task):
        self.tasks.discard(task)
        if not task.cancelled() and task.exception() is not None:
            logging.getLogger('lexvigil').error('Memory-only processing status could not be recorded')

    def current(self, aid, uid, start=False):
        with self.db.begin() as con:
            params = {'id': aid, 'owner': uid, 'now': time.time()}
            valid = "id=:id AND owner=:owner AND status IN ('queued','processing') AND (saved=1 OR expires>:now)"
            if start:
                return con.execute(text("UPDATE analyses SET status='processing' WHERE " + valid), params).rowcount == 1
            return con.execute(text('SELECT id FROM analyses WHERE ' + valid), params).scalar() is not None

    def finish(self, aid, uid, result=None, error=None):
        with self.db.begin() as con:
            con.execute(text("UPDATE analyses SET status=:status,result=:result,error=:error WHERE id=:id AND owner=:owner AND status IN ('queued','processing') AND (saved=1 OR expires>:now)"),
                        {'id': aid, 'owner': uid, 'now': time.time(), 'status': 'failed' if error else 'completed',
                         'result': json.dumps(result) if result is not None else None, 'error': error})

    async def process(self, aid, uid, data, name, language, as_of):
        async def keep_alive():
            return await asyncio.to_thread(self.current, aid, uid)
        try:
            async with self.slots:
                if not await asyncio.to_thread(self.current, aid, uid, True):
                    return
                result = await run_contract(data, name, language, as_of, keep_alive)
                await asyncio.to_thread(self.finish, aid, uid, result)
        except ClaimLost:
            pass
        except asyncio.CancelledError:
            await asyncio.to_thread(self.finish, aid, uid, error='The server stopped during memory-only processing. Please submit again.')
            raise
        except ValueError as exc:
            await asyncio.to_thread(self.finish, aid, uid, error=str(exc)[:300])
        except Exception:
            logging.getLogger('lexvigil').error('Memory-only processing failed')
            await asyncio.to_thread(self.finish, aid, uid, error='Contract processing could not complete. Please retry.')

    async def close(self):
        tasks = tuple(self.tasks)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
