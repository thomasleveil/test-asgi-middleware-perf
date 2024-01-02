import json as python_json
import os

from sanic import Sanic, Request, json

MIDDLEWARE_COUNT = int(os.environ.get('NUM_MIDDLEWARES', '0'))
print("Middlewares to setup: " + str(MIDDLEWARE_COUNT))

app = Sanic("TestServer")


@app.get("/_ping")
async def ping(request):
    return json({"count": 0})


async def my_middleware(request: Request, response):
    if request.path == "/_ping" and response.status == 200:
        data = python_json.loads(response.body)
        response.body = python_json.dumps({"count": data["count"] + 1})


for _ in range(MIDDLEWARE_COUNT):
    app.middleware(my_middleware, "response", priority=0)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=14000)
