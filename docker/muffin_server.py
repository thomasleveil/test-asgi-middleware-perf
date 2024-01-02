import json
import os
from functools import partial

import muffin

MIDDLEWARE_COUNT = int(os.environ.get('NUM_MIDDLEWARES', '0'))
print("Middlewares to setup: " + str(MIDDLEWARE_COUNT))

app = muffin.Application()


@app.route('/', "/_ping")
async def ping(request):
    return muffin.ResponseJSON({"count": 0})


async def my_middleware(app, request: muffin.Request, receive, send):
    if request.url.path != "/_ping":
        return await app(request, receive, send)

    response: muffin.ResponseJSON = await app(request, receive, send)
    data = json.loads(response.content)
    data['count'] += 1
    return muffin.ResponseJSON(data)


for _ in range(MIDDLEWARE_COUNT):
    app.middleware(partial(my_middleware))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=14000)
