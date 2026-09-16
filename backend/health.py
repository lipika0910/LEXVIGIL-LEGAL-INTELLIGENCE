"""Operational probes: liveness is not release approval or dependency readiness."""
from threading import Lock
import time
from sqlalchemy import text
from fastapi import Request
from fastapi.responses import JSONResponse
from .ocr import availability


class DatabaseProbe:
    def __init__(self, db):
        self.db, self.lock = db, Lock()
        self.checked, self.ok = float('-inf'), False

    def ready(self):
        # At most one database query per five seconds per API instance. Never
        # return raw exceptions, connection strings or client data in health output.
        now = time.monotonic()
        if now - self.checked >= 5 and self.lock.acquire(blocking=False):
            try:
                try:
                    with self.db.connect() as con:
                        self.ok = con.execute(text('SELECT 1')).scalar() == 1
                except Exception:
                    self.ok = False
                self.checked = time.monotonic()
            finally:
                self.lock.release()
        return self.ok and time.monotonic() - self.checked < 10


def register_health(app, db, originals, durable_jobs):
    probe = DatabaseProbe(db)

    @app.get('/api/health/live', include_in_schema=False)
    def live():
        return JSONResponse({'status': 'alive'}, headers={'Cache-Control': 'no-store'})

    @app.get('/api/health/ready', include_in_schema=False)
    def ready(request: Request):
        workers = getattr(request.state, 'durable_workers', [])
        checks = {
            'database': probe.ready(),
            'ocr': availability()['available'],
            'original_storage': originals.enabled,
            'durable_processing': durable_jobs.enabled and bool(workers) and all(not task.done() for task in workers),
        }
        healthy = all(checks.values())
        return JSONResponse({'status': 'ready' if healthy else 'not_ready', 'checks': checks},
                            status_code=200 if healthy else 503, headers={'Cache-Control': 'no-store'})
