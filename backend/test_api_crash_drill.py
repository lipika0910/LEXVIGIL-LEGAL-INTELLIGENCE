"""Opt-in Windows integration drill: real HTTP API, real OCR, real process death.

Run with LEXVIGIL_API_DRILL=1. Never connects to the user's preview or database.
"""
import base64
from contextlib import closing
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import socket
import sqlite3
import subprocess
import sys
import time
import httpx
import pytest
from backend.isolated_processing import python_launch, worker_environment
from backend.ocr import availability
from backend.test_isolated_processing import alive

pytestmark = pytest.mark.skipif(
    os.name != 'nt' or os.getenv('LEXVIGIL_API_DRILL') != '1' or not availability()['available'],
    reason='Opt-in Windows full API/OCR crash drill: set LEXVIGIL_API_DRILL=1')


def processes():
    class Entry(ctypes.Structure):
        _fields_ = [('size', wintypes.DWORD), ('usage', wintypes.DWORD), ('pid', wintypes.DWORD),
                    ('heap', ctypes.c_size_t), ('module', wintypes.DWORD), ('threads', wintypes.DWORD),
                    ('parent', wintypes.DWORD), ('priority', wintypes.LONG), ('flags', wintypes.DWORD),
                    ('name', wintypes.WCHAR * 260)]
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
    kernel.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel.CreateToolhelp32Snapshot(2, 0)
    if handle == ctypes.c_void_p(-1).value:
        raise RuntimeError('Process snapshot unavailable')
    rows = {}
    try:
        entry = Entry(); entry.size = ctypes.sizeof(entry)
        valid = kernel.Process32FirstW(handle, ctypes.byref(entry))
        while valid:
            rows[entry.pid] = (entry.parent, entry.name.lower())
            valid = kernel.Process32NextW(handle, ctypes.byref(entry))
    finally:
        kernel.CloseHandle(handle)
    return rows


def descendants(pid):
    rows, found = processes(), set()
    frontier = {pid}
    while frontier:
        children = {p for p, (parent, _) in rows.items() if parent in frontier and p not in found}
        found.update(children)
        frontier = children
    return {p: rows[p][1] for p in found}


class Api:
    def __init__(self, tmp_path):
        with socket.socket() as reservation:
            reservation.bind(('127.0.0.1', 0))
            self.port = reservation.getsockname()[1]
        self.path = tmp_path / 'isolated-api.db'
        self.env = worker_environment()
        self.env.update(DATABASE_URL='sqlite:///' + str(self.path), AUTH_PROVIDER='local',
                        APP_ORIGIN=f'http://127.0.0.1:{self.port}',
                        ORIGINAL_ENCRYPTION_KEY=base64.b64encode(os.urandom(32)).decode())
        self.client = httpx.Client(base_url=f'http://127.0.0.1:{self.port}', timeout=10, trust_env=False)
        self.process = None

    def start(self):
        command, env = python_launch([sys.executable, '-m', 'uvicorn', 'backend.app:app', '--host',
                                     '127.0.0.1', '--port', str(self.port), '--no-access-log', '--log-level', 'error'], self.env)
        self.process = subprocess.Popen(command, env=env, cwd=Path(__file__).resolve().parent.parent,
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                        creationflags=subprocess.CREATE_NO_WINDOW)
        for _ in range(100):
            assert self.process.poll() is None, 'Isolated API exited during startup'
            try:
                response = self.client.get('/api/auth/options')
                if response.status_code == 200:
                    assert response.json()['managed'] is False
                    return
            except httpx.TransportError:
                pass
            time.sleep(.1)
        pytest.fail('Isolated API did not become ready')

    def stop(self):
        if self.process and self.process.poll() is None:
            # This handle belongs exclusively to this test's API interpreter.
            self.process.kill()
            self.process.wait(timeout=10)

    def rows(self, sql, args=()):
        with closing(sqlite3.connect(self.path)) as con:
            return con.execute(sql, args).fetchall()

    def register(self, email='crash-drill@example.com'):
        response = self.client.post('/api/auth/register', json={
            'email': email, 'password': 'synthetic-crash-password-2026'})
        assert response.status_code == 200


@pytest.fixture
def api(tmp_path):
    instance = Api(tmp_path)
    try:
        instance.start()
        instance.register()
        yield instance
    finally:
        instance.stop()
        instance.client.close()


def scanned_contract():
    import pymupdf
    from backend.test_ocr import scan
    page = scan('1.1 Payment\nPayment must be made within thirty days.')
    with pymupdf.open(stream=page, filetype='pdf') as source, pymupdf.open() as document:
        for _ in range(12):
            document.insert_pdf(source)
        return document.tobytes(deflate=True)


@pytest.mark.parametrize('consent', [True, False], ids=['durable-recovery', 'memory-only-no-replay'])
def test_api_crash_during_real_ocr(api, consent):
    response = api.client.post('/api/contracts/analyze',
        files={'file': ('synthetic-scan.pdf', scanned_contract(), 'application/pdf')},
        data={'store_original': str(consent).lower(), 'ocr_language': 'eng'})
    assert response.status_code == 202
    aid = response.json()['id']
    expiry = api.rows('SELECT expires FROM analyses WHERE id=?', (aid,))[0][0]
    original = api.rows('SELECT expires,payload FROM originals WHERE analysis_id=?', (aid,))
    if consent:
        assert original and original[0][1].startswith(b'LVENC1')
        digest = hashlib.sha256(original[0][1]).hexdigest()
    else:
        assert not original
        assert api.rows('SELECT count(*) FROM contract_jobs')[0][0] == 0

    observed = {}
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        observed = descendants(api.process.pid)
        if 'tesseract.exe' in observed.values():
            break
        assert api.process.poll() is None
        time.sleep(.01)
    assert 'tesseract.exe' in observed.values(), 'Real OCR was not observed before the crash'
    api.stop()
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and any(alive(pid) for pid in observed):
        time.sleep(.02)
    assert not any(alive(pid) for pid in observed), 'Processor or OCR survived API death'

    api.start()  # Same temporary database/key; actual default 30-second claim lease.
    deadline = time.monotonic() + 65
    while time.monotonic() < deadline:
        response = api.client.get('/api/analyses/' + aid)
        assert response.status_code == 200
        report = response.json()
        if report['status'] in ('completed', 'failed'):
            break
        time.sleep(.2)
    assert api.rows('SELECT expires FROM analyses WHERE id=?', (aid,))[0][0] == expiry
    if consent:
        assert report['status'] == 'completed', report.get('error')
        assert report['result']['document']['extraction_method'] == 'pdf_ocr_mixed'
        assert len(report['result']['document']['units']) == 12
        assert api.rows('SELECT state,attempts FROM contract_jobs WHERE id=?', (aid,)) == [('done', 2)]
        after = api.rows('SELECT expires,payload FROM originals WHERE analysis_id=?', (aid,))[0]
        assert after[0] == original[0][0] and hashlib.sha256(after[1]).hexdigest() == digest
        assert api.rows('SELECT count(*) FROM analyses WHERE id=?', (aid,)) == [(1,)]
    else:
        assert report['status'] == 'failed' and 'memory-only' in report['error']
        assert report['result'] is None and report['processing']['durable'] is False
        assert api.rows('SELECT count(*) FROM originals') == [(0,)]
        assert api.rows('SELECT count(*) FROM contract_jobs') == [(0,)]


def test_repeated_upload_preview_and_deletion_stability(api):
    from backend.test_ocr import scan
    scan_bytes=scan('1.1 Payment\nPayment must be made within thirty days.')
    text_bytes=b'1.1 Services\nThe supplier shall provide services.\n2.1 Payment\nPayment is due in 30 days.'
    api_pid=api.process.pid
    completed=0
    for account in range(4):
        if account:
            assert api.client.post('/api/logout').status_code==200
            api.register(f'stability-{account}@example.com')
        for batch in range(4):
            pending=[]
            for slot in range(2):
                index=batch*2+slot
                scanned=index%4==0
                consent=index%3!=1
                data=scan_bytes if scanned else text_bytes
                response=api.client.post('/api/contracts/analyze',
                    files={'file':('synthetic.pdf' if scanned else 'synthetic.txt',data,'application/pdf' if scanned else 'text/plain')},
                    data={'store_original':str(consent).lower(),'ocr_language':'eng' if scanned else ''})
                assert response.status_code==202,response.text
                pending.append((response.json()['id'],scanned,consent,data))
            for aid,scanned,consent,data in pending:
                deadline=time.monotonic()+20
                while time.monotonic()<deadline:
                    response=api.client.get('/api/analyses/'+aid)
                    assert response.status_code==200
                    report=response.json()
                    if report['status'] in ('completed','failed'): break
                    time.sleep(.05)
                assert report['status']=='completed',report.get('error')
                assert report['processing']['durable'] is consent
                base='/api/analyses/'+aid+'/original'
                assert api.client.get(base).json()['available'] is consent
                if consent:
                    original=api.client.get(base+'/download')
                    assert original.status_code==200 and original.content==data
                    if scanned:
                        preview=api.client.get(base+'/pages/1')
                        assert preview.status_code==200 and preview.content.startswith(b'\x89PNG')
                    assert api.client.delete(base).status_code==200
                    assert api.client.get(base).json()['available'] is False
                    assert api.client.get('/api/analyses/'+aid).status_code==200
                assert api.client.delete('/api/analyses/'+aid).status_code==200
                assert api.client.get('/api/analyses/'+aid).status_code==404
                completed+=1
                assert api.process.poll() is None and api.process.pid==api_pid
        assert api.rows('SELECT count(*) FROM analyses')==[(0,)]
        assert api.rows('SELECT count(*) FROM originals')==[(0,)]
    assert completed==32
