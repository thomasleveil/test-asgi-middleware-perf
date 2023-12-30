import os
import sys

import falcon.asgi
from falcon.asgi import Response

# Default value for middleware count
MIDDLEWARE_COUNT = 1

# Check if an argument is provided
try:
    MIDDLEWARE_COUNT = int(os.environ['NUM_MIDDLEWARES'])
except ValueError:
    print("Please provide a valid integer for middleware count")
    sys.exit(1)

print("Middlewares to setup: " + str(MIDDLEWARE_COUNT))


async def middleware_one(request, handler):
    response = await handler(request)
    response.status_code += 1
    return response


class PingResource:

    async def on_get(self, req, resp):
        resp.media = "pong"
        resp.status = 200


class DummyMiddleware:
    async def process_response(self, req, resp: Response, resource, req_succeeded):
        resp.status += 1


app = falcon.asgi.App(middleware=[
    DummyMiddleware()
    for _ in range(MIDDLEWARE_COUNT)
])
app.add_route('/_ping', PingResource())

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=14000)
