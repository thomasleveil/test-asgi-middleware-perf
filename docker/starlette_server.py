import json
import os

from starlette.applications import Starlette
from starlette.datastructures import MutableHeaders
from starlette.middleware import Middleware
from starlette.responses import JSONResponse
from starlette.routing import Route

MIDDLEWARE_COUNT = int(os.environ.get('NUM_MIDDLEWARES', '0'))
print("Middlewares to setup: " + str(MIDDLEWARE_COUNT))


class ASGIMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http' and scope['path'] == '/_ping':
            original_send = send
            initial_message = None
            body = b""

            async def send_wrapper(message) -> None:
                nonlocal body, initial_message
                if message['type'] == 'http.response.start':
                    initial_message = message
                elif message['type'] == 'http.response.body':
                    body += message.get('body', b"")
                    if not message.get('more_body', False):
                        data = json.loads(body.decode())
                        body = json.dumps({"count": data['count'] + 1}).encode()

                        headers = MutableHeaders(raw=initial_message["headers"])
                        headers["Content-Length"] = str(len(body))
                        await original_send(initial_message)
                        await original_send({
                            "type": "http.response.body",
                            "body": body,
                        })

            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)


async def ping(request):
    return JSONResponse({"count": 0})


app = Starlette(
    routes=[
        Route("/_ping", endpoint=ping),
    ],
    middleware=[Middleware(ASGIMiddleware)] * MIDDLEWARE_COUNT,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=14000)
