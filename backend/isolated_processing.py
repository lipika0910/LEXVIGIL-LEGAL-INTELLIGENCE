"""Cancellable, bounded local contract subprocess supervision."""
import asyncio
import json
import logging
import os
from pathlib import Path
import subprocess
import sys
from .process_limits import ProcessTree
from .isolated_worker import MAX_INPUT, MAX_OUTPUT

PROCESSING_SECONDS = 660  # 20 OCR pages x 30 seconds, plus parsing allowance.
HEARTBEAT_SECONDS = 5


class ClaimLost(Exception):
    pass


def python_launch(command, env):
    """Match CPython multiprocessing: bypass the Windows venv redirector.

    The process receiving containment must be the real interpreter, not a
    wrapper that may already have created an uncontained child.
    """
    command, env = list(command), dict(env)
    if os.name == 'nt' and sys.prefix != sys.base_prefix and os.path.normcase(command[0]) == os.path.normcase(sys.executable):
        command[0] = sys._base_executable
        env['__PYVENV_LAUNCHER__'] = sys.executable
    return command, env


def worker_environment():
    allowed = {'systemroot', 'windir', 'path', 'temp', 'tmp', 'lang', 'lc_all',
               'tesseract_cmd', 'tessdata_prefix'}
    env = {k: v for k, v in os.environ.items() if k.lower() in allowed}
    env.update(PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1', OMP_THREAD_LIMIT='1')
    # Hosted runtimes add vendored dependencies to sys.path at startup. A new
    # interpreter does not inherit those additions. Forward resolved import
    # directories from this trusted interpreter, never the raw environment or
    # any document-supplied paths. Keep credentials excluded above.
    env['PYTHONPATH'] = os.pathsep.join(dict.fromkeys(
        str(Path(entry).resolve()) for entry in sys.path
        if isinstance(entry, str) and entry and Path(entry).is_absolute()
    ))
    return env


async def run_contract(data, name, language='', as_of=None, keep_alive=None):
    if not 0 < len(data) <= MAX_INPUT:
        raise ValueError('Invalid document size.')
    header = json.dumps({'size': len(data), 'name': name, 'language': language, 'as_of': as_of}).encode() + b'\n'
    if len(header) > 8192:
        raise ValueError('Document filename is too long.')
    return await _run([sys.executable, '-m', 'backend.isolated_worker'], header + data, keep_alive)


async def _run(command, payload, keep_alive=None, timeout=PROCESSING_SECONDS, heartbeat=HEARTBEAT_SECONDS):
    command, env = python_launch(command, worker_environment())
    options = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {'start_new_session': True}
    launch = asyncio.create_task(asyncio.create_subprocess_exec(
        *command, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL, cwd=Path(__file__).resolve().parent.parent,
        env=env, **options))
    process = tree = None
    tasks = []
    try:
        # Shield creation so shutdown cannot lose track of a newly created child.
        process = await asyncio.shield(launch)
        tree = ProcessTree(process.pid)
        async def send():
            try:
                process.stdin.write(payload)
                await process.stdin.drain()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                process.stdin.close()
        async def receive():
            chunks, size = [], 0
            while chunk := await process.stdout.read(65536):
                size += len(chunk)
                if size > MAX_OUTPUT:
                    raise ValueError('The analysis exceeded the response size limit.')
                chunks.append(chunk)
            return b''.join(chunks)
        tasks = [asyncio.create_task(send()), asyncio.create_task(receive()), asyncio.create_task(process.wait())]
        io_tasks = tuple(tasks)
        async def collect():
            values = await asyncio.gather(*io_tasks)
            if values[2] != 0:
                raise ValueError('The isolated processor stopped unexpectedly or exceeded its resource limits. Please retry.')
            try:
                response = json.loads(values[1])
                if not isinstance(response, dict):
                    raise ValueError()
            except (ValueError, UnicodeDecodeError):
                raise ValueError('The isolated processor returned an invalid response.') from None
            if response.get('error'):
                if response.get('failure_kind') in ('dependency_missing', 'memory_limit'):
                    logging.getLogger(__name__).warning('Contract worker failure: %s', response['failure_kind'])
                raise ValueError(str(response['error'])[:300])
            if not isinstance(response.get('result'), dict):
                raise ValueError('The isolated processor returned an invalid result.')
            return response['result']
        result = asyncio.create_task(collect())
        tasks.append(result)
        deadline = asyncio.get_running_loop().time() + timeout
        while True:
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                raise ValueError('Contract processing exceeded the total time limit. Split the document and retry.')
            done, _ = await asyncio.wait([result], timeout=min(heartbeat, remaining))
            if done:
                return result.result()
            if keep_alive is not None and not await keep_alive():
                raise ClaimLost()
    finally:
        if process is None:
            process = await launch
        if process.stdin is not None:
            process.stdin.close()
        if tree is not None:
            tree.close()
        if process.returncode is None:
            try:
                process.kill()
            except ProcessLookupError:
                pass
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        # Drain residual bytes after killing the tree; a paused pipe transport
        # must not prevent process.wait() from observing shutdown.
        while await process.stdout.read(65536):
            pass
        await process.wait()
