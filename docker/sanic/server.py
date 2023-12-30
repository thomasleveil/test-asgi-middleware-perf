import os
import sys

from sanic import Sanic
from sanic.response import text

# Default value for middleware count
MIDDLEWARE_COUNT = 1

# Check if an argument is provided
try:
    MIDDLEWARE_COUNT = int(os.environ['NUM_MIDDLEWARES'])
except ValueError:
    print("Please provide a valid integer for middleware count")
    sys.exit(1)

print("Middlewares to setup: " + str(MIDDLEWARE_COUNT))

app = Sanic("TestServer")


@app.get("/_ping")
async def ping(request):
    return text("pong")


async def dummy_middleware(request, response):
    response.status += 1


for _ in range(MIDDLEWARE_COUNT):
    app.middleware(dummy_middleware, "response", priority=0)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=14000)
