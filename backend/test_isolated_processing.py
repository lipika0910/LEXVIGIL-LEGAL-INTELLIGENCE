import asyncio
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import pytest
from backend.isolated_processing import _run, run_contract, ClaimLost, worker_environment


def alive(pid):
    if os.name == 'nt':
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel.WaitForSingleObject.restype = wintypes.DWORD
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x00100000, False, pid)
        if not handle:
            return False
        try:
            return kernel.WaitForSingleObject(handle, 0) == 258
        finally:
            kernel.CloseHandle(handle)
    try:
        os.kill(pid, 0)
        status = Path(f'/proc/{pid}/stat')
        return not status.exists() or status.read_text().split()[2] != 'Z'
    except ProcessLookupError:
        return False


TREE_PROGRAM = '''
import sys, subprocess, time, json, os
from pathlib import Path
sys.stdin.buffer.read()
child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)'])
marker=Path(sys.argv[1])
pending=marker.with_suffix('.pending')
pending.write_text(json.dumps([os.getpid(),child.pid]))
pending.replace(marker)
time.sleep(60)
'''


@pytest.mark.parametrize('reason', ['cancel', 'timeout', 'lease'])
def test_stopped_work_terminates_parser_and_descendant(tmp_path, reason):
    marker = tmp_path / 'synthetic-pids.json'
    async def run():
        retain = True
        async def keep_alive():
            return retain
        task = asyncio.create_task(_run([sys.executable, '-c', TREE_PROGRAM, str(marker)], b'go',
                                        keep_alive, timeout=1.5 if reason == 'timeout' else 10, heartbeat=.05))
        try:
            for _ in range(100):
                if marker.exists():
                    break
                await asyncio.sleep(.02)
            assert marker.exists(), 'Synthetic process tree did not start'
            pids = json.loads(marker.read_text())
            assert all(alive(pid) for pid in pids)
            if reason == 'cancel':
                task.cancel()
                expected = asyncio.CancelledError
            elif reason == 'lease':
                retain = False
                expected = ClaimLost
            else:
                expected = ValueError
            with pytest.raises(expected):
                await asyncio.wait_for(task, 5)
            for _ in range(50):
                if not any(alive(pid) for pid in pids):
                    break
                await asyncio.sleep(.02)
            assert not any(alive(pid) for pid in pids)
        finally:
            if not task.done():
                task.cancel()
            await asyncio.gather(task, return_exceptions=True)
    asyncio.run(run())


def test_real_contract_uses_child_and_returns_evidence():
    result = asyncio.run(run_contract(b'1.1 Services\nThe supplier shall provide services.', 'test.txt'))
    assert result['kind'] == 'contract' and result['clauses']


def test_launched_pid_is_actual_interpreter_and_venv_is_preserved():
    from backend.isolated_processing import python_launch
    command,env=python_launch([sys.executable,'-c',"import os,sys,json;print(json.dumps([os.getpid(),sys.prefix]))"],worker_environment())
    with subprocess.Popen(command,env=env,stdout=subprocess.PIPE,text=True) as child:
        actual,prefix=json.loads(child.stdout.read())
        assert actual==child.pid
        assert os.path.normcase(prefix)==os.path.normcase(sys.prefix)
        assert child.wait(timeout=5)==0


def test_real_ocr_runs_inside_containment():
    from backend.ocr import availability
    from backend.test_ocr import scan
    if not availability()['available']:
        pytest.skip('Local OCR runtime required')
    data=scan('1.1 Payment\nPayment must be made within thirty days.')
    result=asyncio.run(run_contract(data,'scan.pdf','eng'))
    assert result['document']['extraction_method']=='pdf_ocr_mixed'
    assert 'Payment' in result['document']['units'][0]['text']


def test_worker_environment_excludes_credentials(monkeypatch):
    monkeypatch.setenv('SUPABASE_SERVICE_ROLE_KEY', 'synthetic-secret')
    monkeypatch.setenv('DATABASE_URL', 'synthetic-database')
    monkeypatch.setenv('ORIGINAL_ENCRYPTION_KEY', 'synthetic-secret')
    assert not any(key in worker_environment() for key in
                   ('SUPABASE_SERVICE_ROLE_KEY', 'DATABASE_URL', 'ORIGINAL_ENCRYPTION_KEY'))
    code = "import sys,os,json;sys.stdin.buffer.read();print(json.dumps({'result':{'secret':os.getenv('ORIGINAL_ENCRYPTION_KEY')}}))"
    assert asyncio.run(_run([sys.executable, '-c', code], b'')) == {'secret': None}


def test_worker_inherits_runtime_dependency_paths_without_raw_pythonpath(tmp_path, monkeypatch):
    vendor = tmp_path / 'runtime-vendor'
    vendor.mkdir()
    (vendor / 'synthetic_hosted_dependency.py').write_text('VALUE = 42', encoding='utf-8')
    monkeypatch.syspath_prepend(str(vendor))
    monkeypatch.setenv('PYTHONPATH', 'untrusted-environment-path')
    monkeypatch.setenv('LEXVIGIL_DB_AUTH_PASSWORD', 'synthetic-password')
    code = "import sys,os,json;sys.stdin.buffer.read();import synthetic_hosted_dependency as d;print(json.dumps({'result':{'value':d.VALUE,'secret':os.getenv('LEXVIGIL_DB_AUTH_PASSWORD')}}))"
    assert asyncio.run(_run([sys.executable, '-c', code], b'')) == {'value': 42, 'secret': None}
    assert 'untrusted-environment-path' not in worker_environment()['PYTHONPATH']


@pytest.mark.parametrize('output', ['not-json', '[]', '{"result":false}'])
def test_invalid_child_response_fails_closed(output):
    code = 'import sys;sys.stdin.buffer.read();print(' + repr(output) + ')'
    with pytest.raises(ValueError, match='invalid'):
        asyncio.run(_run([sys.executable, '-c', code], b''))


def test_output_limit_stops_noisy_child(monkeypatch):
    monkeypatch.setattr('backend.isolated_processing.MAX_OUTPUT', 1024)
    code = "import sys;sys.stdin.buffer.read();sys.stdout.write('x'*1000000);sys.stdout.flush()"
    with pytest.raises(ValueError, match='response size'):
        asyncio.run(_run([sys.executable, '-c', code], b'', timeout=5))


def test_containment_failure_closes_child_before_sending_input(tmp_path,monkeypatch):
    marker=tmp_path/'not-started.json'
    pids=[]
    def fail(pid):
        pids.append(pid)
        raise RuntimeError('Synthetic containment failure')
    monkeypatch.setattr('backend.isolated_processing.ProcessTree',fail)
    with pytest.raises(RuntimeError,match='containment'):
        asyncio.run(_run([sys.executable,'-c',TREE_PROGRAM,str(marker)],b'go'))
    assert pids and not any(alive(pid) for pid in pids)
    assert not marker.exists()


@pytest.mark.skipif(os.name != 'nt',reason='Windows aggregate Job Object memory limit')
def test_windows_job_memory_limit():
    from backend.process_limits import MEMORY_BYTES
    code='''
import sys,json
sys.stdin.buffer.read()
try:
    allocation=bytearray(int(sys.argv[1]))
    limited=False
except MemoryError:
    limited=True
print(json.dumps({'result':{'limited':limited}}))
'''
    assert asyncio.run(_run([sys.executable,'-c',code,str(MEMORY_BYTES)],b''))=={'limited':True}


@pytest.mark.skipif(os.name != 'nt', reason='Windows Job Object parent-death containment')
def test_supervisor_crash_terminates_its_process_tree(tmp_path):
    marker = tmp_path / 'orphan-check.json'
    code = '''
import asyncio, os, sys
from pathlib import Path
from backend.isolated_processing import _run
async def main():
    task=asyncio.create_task(_run([sys.executable,'-c',sys.argv[2],sys.argv[1]],b'go'))
    for _ in range(200):
        if Path(sys.argv[1]).exists(): os._exit(23)
        await asyncio.sleep(.02)
    raise RuntimeError('Synthetic tree did not start')
asyncio.run(main())
'''
    result = subprocess.run([sys.executable, '-c', code, str(marker), TREE_PROGRAM],
                            capture_output=True, timeout=10)
    assert result.returncode == 23
    pids = json.loads(marker.read_text())
    for _ in range(100):
        if not any(alive(pid) for pid in pids):
            break
        time.sleep(.02)
    assert not any(alive(pid) for pid in pids)
