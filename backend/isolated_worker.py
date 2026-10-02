"""One contract per process. Input and output stay in pipes; no app/DB imports."""
import json
import os
import sys

MAX_INPUT = 15 * 1024 * 1024
MAX_OUTPUT = 32 * 1024 * 1024


def main():
    # The parent attaches containment before writing this header. Do not import
    # document parsers or spawn OCR until the complete request has arrived.
    try:
        header = sys.stdin.buffer.readline(8193)
        if len(header) > 8192 or not header.endswith(b'\n'):
            raise ValueError('Invalid processing request.')
        request = json.loads(header)
        size = request['size']
        if not isinstance(size, int) or not 0 < size <= MAX_INPUT:
            raise ValueError('Invalid document size.')
        data = sys.stdin.buffer.read(size + 1)
        if len(data) != size:
            raise ValueError('Incomplete processing request.')
        if os.name != 'nt':
            import resource
            from .process_limits import MEMORY_BYTES
            resource.setrlimit(resource.RLIMIT_AS, (MEMORY_BYTES, MEMORY_BYTES))
            resource.setrlimit(resource.RLIMIT_CPU, (660, 660))
        from .engine import analyze, extract
        result = analyze(extract(data, request['name'], request['language']), request['name'], request['as_of'])
        output = json.dumps({'result': result}, ensure_ascii=False).encode('utf-8')
        if len(output) > MAX_OUTPUT:
            raise ValueError('The analysis exceeded the response size limit. Split the document and retry.')
    except ValueError as exc:
        output = json.dumps({'error': str(exc)[:300]}).encode('utf-8')
    except ModuleNotFoundError:
        output = b'{"error":"Contract processing is temporarily unavailable. Please retry later.","failure_kind":"dependency_missing"}'
    except MemoryError:
        output = b'{"error":"Contract processing exceeded its memory limit. Split the document and retry.","failure_kind":"memory_limit"}'
    except Exception:
        output = b'{"error":"Contract processing could not complete. Check the original and retry."}'
    sys.stdout.buffer.write(output)
    sys.stdout.buffer.flush()


if __name__ == '__main__':
    main()
