import sys

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from starlette.requests import Request
from starlette.types import ASGIApp, Scope, Receive, Send

# Default value for middleware count
MIDDLEWARE_COUNT = 1

# Check if an argument is provided
if len(sys.argv) > 1:
    try:
        MIDDLEWARE_COUNT = int(sys.argv[1])
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


async def my_middleware(request: Request, call_next):
    response = await call_next(request)
    response.status_code += 1
    return response


@app.get("/_ping", response_class=PlainTextResponse)
async def ping():
    return "pong"


for _ in range(MIDDLEWARE_COUNT):
    app.middleware("http")(my_middleware)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=14000)
