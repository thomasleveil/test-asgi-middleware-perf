import os

import falcon.asgi
from falcon.asgi import Response

MIDDLEWARE_COUNT = int(os.environ.get('NUM_MIDDLEWARES', '0'))
print("Middlewares to setup: " + str(MIDDLEWARE_COUNT))


class PingResource:

    async def on_get(self, req, resp):
        resp.media = {"count": 0}
        resp.status = 200


class DummyMiddleware:
    async def process_response(self, req, resp: Response, resource, req_succeeded):
        resp.media["count"] += 1


app = falcon.asgi.App(middleware=[
    DummyMiddleware()
    for _ in range(MIDDLEWARE_COUNT)
])
app.add_route('/_ping', PingResource())

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=14000)
