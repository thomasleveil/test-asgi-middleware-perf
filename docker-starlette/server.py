import json
import resource
import sys
from pathlib import Path

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse, FileResponse
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


class TestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, req: Request, call_next: RequestResponseEndpoint):
        return await call_next(req)


async def ping(request):
    return PlainTextResponse("pong")


app = Starlette(
    routes=[
        Route("/_ping", endpoint=ping),
    ],
    middleware=[Middleware(TestMiddleware)] * MIDDLEWARE_COUNT,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=14000)
