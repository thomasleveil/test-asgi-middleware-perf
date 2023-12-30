import sys

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import PlainTextResponse
from starlette.routing import Route

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


class ASGIMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] == 'http':
            original_send = send

            async def send_wrapper(message) -> None:
                if message['type'] == 'http.response.start':
                    message['status'] += 1
                await original_send(message)

            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)


async def ping(request):
    return PlainTextResponse("pong")


app = Starlette(
    routes=[
        Route("/_ping", endpoint=ping),
    ],
    middleware=[Middleware(ASGIMiddleware)] * MIDDLEWARE_COUNT,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=14000)
