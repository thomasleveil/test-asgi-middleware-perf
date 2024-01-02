import os

from blacksheep import Application, get, json

MIDDLEWARE_COUNT = int(os.environ.get('NUM_MIDDLEWARES', '0'))
print("Middlewares to setup: " + str(MIDDLEWARE_COUNT))


@get("/_ping")
async def ping():
    return json({"count": 0})


async def middleware_one(request, handler):
    response = await handler(request)
    data = await response.json()
    return json({"count": data["count"] + 1})


app = Application()
for _ in range(MIDDLEWARE_COUNT):
    app.middlewares.append(middleware_one)

print(app.middlewares)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=14000)
