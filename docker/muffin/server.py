import os
import sys
from functools import partial

import muffin

# Default value for middleware count
MIDDLEWARE_COUNT = 1

# Check if an argument is provided
try:
    MIDDLEWARE_COUNT = int(os.environ['NUM_MIDDLEWARES'])
except ValueError:
    print("Please provide a valid integer for middleware count")
    sys.exit(1)

print("Middlewares to setup: " + str(MIDDLEWARE_COUNT))

app = muffin.Application()


@app.route('/', "/_ping")
async def ping(request):
    return "pong"


async def dummy_middleware(app, request, receive, send):
    response = await app(request, receive, send)
    response.status_code += 1
    return response


for _ in range(MIDDLEWARE_COUNT):
    app.middleware(partial(dummy_middleware))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=14000)
