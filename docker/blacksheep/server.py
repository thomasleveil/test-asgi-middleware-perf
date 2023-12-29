import sys

from blacksheep import Application, get

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


@get("/_ping")
async def ping():
    return "pong"


async def middleware_one(request, handler):
    response = await handler(request)
    response.status = response.status + 1
    return response


app = Application()
for _ in range(MIDDLEWARE_COUNT):
    app.middlewares.append(middleware_one)

print(app.middlewares)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=14000)
