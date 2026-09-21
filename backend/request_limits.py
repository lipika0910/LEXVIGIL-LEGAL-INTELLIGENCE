"""Bound request bytes before multipart parsing, including chunked bodies."""
from starlette.responses import JSONResponse


class RequestBodyLimit:
    def __init__(self, app, maximum):
        self.app, self.maximum = app, maximum

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope['method'] not in ('POST','PUT','PATCH','DELETE'):
            return await self.app(scope, receive, send)
        parts, size = [], 0
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect': return
            chunk = message.get('body', b'')
            size += len(chunk)
            if size > self.maximum:
                response = JSONResponse({'detail':'Request exceeds the showcase upload limit.'},
                    status_code=413, headers={'Cache-Control':'no-store'})
                return await response(scope, receive, send)
            parts.append(chunk)
            if not message.get('more_body', False): break
        body = b''.join(parts)
        delivered = False

        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {'type':'http.request', 'body':body, 'more_body':False}
            return await receive()

        return await self.app(scope, replay, send)
