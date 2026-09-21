"""Text-only, 20-second isolated worker invocation for the reduced demo."""
import json
import sys
from .isolated_processing import _run


async def process_contract(data, name, as_of=None):
    if not 0 < len(data) <= 2 * 1024 * 1024:
        raise ValueError('Showcase documents must be nonempty and at most 2 MB.')
    header = json.dumps({'size':len(data), 'name':name, 'language':'', 'as_of':as_of}).encode() + b'\n'
    if len(header) > 8192:
        raise ValueError('Document filename is too long.')
    return await _run([sys.executable, '-m', 'backend.isolated_worker'], header+data, timeout=20)
