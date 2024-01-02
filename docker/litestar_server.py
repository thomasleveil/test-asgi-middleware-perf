import json
import os

from litestar import Litestar, get
from litestar.datastructures import MutableScopeHeaders
from litestar.types import Scope, Receive, Send, ASGIApp, Message, HTTPResponseStartEvent

MIDDLEWARE_COUNT = int(os.environ.get('NUM_MIDDLEWARES', '0'))
print("Middlewares to setup: " + str(MIDDLEWARE_COUNT))


def middleware_factory(app: ASGIApp) -> ASGIApp:
    async def my_middleware(scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] == 'http' and scope['path'] == '/_ping':
            original_send = send
            initial_message: HTTPResponseStartEvent
            body = b""

            async def send_wrapper(message: Message) -> None:
                nonlocal body, initial_message
                if message['type'] == 'http.response.start':
                    initial_message = message
                elif message['type'] == 'http.response.body':
                    body += message.get('body', b"")
                    if not message.get('more_body', False):
                        data = json.loads(body.decode())
                        body = json.dumps({"count": data['count'] + 1}).encode()

                        headers = MutableScopeHeaders.from_message(message=initial_message)
                        headers["Content-Length"] = str(len(body))
                        await original_send(initial_message)
                        await original_send({
                            "type": "http.response.body",
                            "body": body,
                        })

            await app(scope, receive, send_wrapper)
        else:
            await app(scope, receive, send)

    return my_middleware


@get("/_ping")
async def ping() -> dict:
    return {"count": 0}


app = Litestar(
    route_handlers=[ping],
    middleware=[middleware_factory] * MIDDLEWARE_COUNT,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=14000)
