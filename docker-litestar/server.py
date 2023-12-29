import sys

from litestar import Litestar, get
from litestar.middleware import AbstractMiddleware
from litestar.types import Scope, Receive, Send, ASGIApp

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

def middleware_factory(app: ASGIApp) -> ASGIApp:
    async def my_middleware(scope: Scope, receive: Receive, send: Send) -> None:
        # do something here
        ...
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
