import os
import sys

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from starlette.types import ASGIApp, Scope, Receive, Send

# Default value for middleware count
MIDDLEWARE_COUNT = 1

# Check if an argument is provided
try:
    MIDDLEWARE_COUNT = int(os.environ['NUM_MIDDLEWARES'])
except ValueError:
    print("Please provide a valid integer for middleware count")
    sys.exit(1)

print("Middlewares to setup: " + str(MIDDLEWARE_COUNT))


class MyMiddleware:
    def __init__(self, app: ASGIApp, ) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] == 'http':
            original_send = send

            async def send_wrapper(message) -> None:
                if message['type'] == 'http.response.start':
                    message['status'] += 1
                await original_send(message)

            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)


app = FastAPI()


@app.get("/_ping", response_class=PlainTextResponse)
async def ping():
    return "pong"


for _ in range(MIDDLEWARE_COUNT):
    app.add_middleware(MyMiddleware)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=14000)
