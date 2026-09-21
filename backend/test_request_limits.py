import asyncio
from backend.request_limits import RequestBodyLimit


def test_chunked_limit_before_application():
    called, sent = [], []
    async def app(*args): called.append(True)
    chunks = iter([{'type':'http.request','body':b'123','more_body':True},
                   {'type':'http.request','body':b'456','more_body':False}])
    async def receive(): return next(chunks)
    async def send(value): sent.append(value)
    asyncio.run(RequestBodyLimit(app,5)({'type':'http','method':'POST'}, receive, send))
    assert not called and sent[0]['status'] == 413


def test_body_is_replayed_exactly():
    seen = []
    async def app(scope, receive, send): seen.append(await receive())
    chunks = iter([{'type':'http.request','body':b'12','more_body':True},
                   {'type':'http.request','body':b'345','more_body':False}])
    async def receive(): return next(chunks)
    async def send(value): pass
    asyncio.run(RequestBodyLimit(app,5)({'type':'http','method':'POST'}, receive, send))
    assert seen == [{'type':'http.request','body':b'12345','more_body':False}]
