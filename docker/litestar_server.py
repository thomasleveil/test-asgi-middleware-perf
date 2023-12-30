import os
import sys

from litestar import Litestar, get
from litestar.types import Scope, Receive, Send, ASGIApp, Message

# Default value for middleware count
MIDDLEWARE_COUNT = 1

# Check if an argument is provided
try:
    MIDDLEWARE_COUNT = int(os.environ['NUM_MIDDLEWARES'])
except ValueError:
    print("Please provide a valid integer for middleware count")
    sys.exit(1)

print("Middlewares to setup: " + str(MIDDLEWARE_COUNT))

def middleware_factory(app: ASGIApp) -> ASGIApp:
    async def my_middleware(scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] == 'http':
            original_send = send
            async def send_wrapper(message: Message) -> None:
                if message['type'] == 'http.response.start':
                    message['status'] += 1
                await original_send(message)
            await app(scope, receive, send_wrapper)
        else:
            await app(scope, receive, send)

    return my_middleware

@get("/_ping")
async def ping() -> str:
    return "pong"


app = Litestar(
    route_handlers=[ping],
    middleware=[middleware_factory] * MIDDLEWARE_COUNT,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=14000)
