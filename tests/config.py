from utils.models import AsgiServerEnv

num_middlewares = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

test_matrix: list[AsgiServerEnv] = [
    AsgiServerEnv(
        asgi_module="starlette",
        asgi_version="0.34.0",
        python="3.12.1",
        uvicorn="0.25.0",
        gunicorn="21.2.0",
    ),
    AsgiServerEnv(
        asgi_module="blacksheep",
        asgi_version="2.0.4",
        python="3.12.1",
        uvicorn="0.25.0",
        gunicorn="21.2.0",
    ),
    AsgiServerEnv(
        asgi_module="falcon",
        asgi_version="3.1.3",
        python="3.12.1",
        uvicorn="0.25.0",
        gunicorn="21.2.0",
    ),
    AsgiServerEnv(
        asgi_module="fastapi",
        asgi_version="0.108.0",
        python="3.12.1",
        uvicorn="0.25.0",
        gunicorn="21.2.0",
    ),
    AsgiServerEnv(
        asgi_module="litestar",
        asgi_version="2.4.5",
        python="3.12.1",
        uvicorn="0.25.0",
        gunicorn="21.2.0",
    ),
    AsgiServerEnv(
        asgi_module="muffin",
        asgi_version="0.100.1",
        python="3.12.1",
        uvicorn="0.25.0",
        gunicorn="21.2.0",
    ),
    AsgiServerEnv(
        asgi_module="sanic",
        asgi_version="23.12.0",
        python="3.12.1",
        uvicorn="0.25.0",
        gunicorn="21.2.0",
    ),
]
