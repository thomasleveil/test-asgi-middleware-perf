import time
from datetime import datetime
from pathlib import Path

import pytest
from python_on_whales import DockerClient

from utils import extract_transaction_rate
from utils.docker import get_docker_image
from utils.models import AsgiServerEnv

####################################################
num_middlewares = range(17)
test_matrix: list[AsgiServerEnv] = [
    AsgiServerEnv(
        asgi_module="starlette",
        asgi_version="0.34.0",
        python="3.12.1",
        uvicorn="0.25.0",
        gunicorn="21.2.0",
    ),
    # AsgiServerEnv(
    #     asgi_module="starlette",
    #     asgi_version="0.34.0",
    #     python="3.13.0a2",
    #     uvicorn="0.25.0",
    #     gunicorn="21.2.0",
    # ),
    AsgiServerEnv(
        asgi_module="blacksheep",
        asgi_version="2.0.3",
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
        asgi_version="23.6.0",
        python="3.12.1",
        uvicorn="0.25.0",
        gunicorn="21.2.0",
    ),
]
####################################################

now = datetime.now()
docker = DockerClient()


@pytest.mark.flaky(max_runs=4)
@pytest.mark.parametrize(
    "num_middlewares", num_middlewares, ids=lambda x: f"middlewares-{x:02}"
)
@pytest.mark.parametrize("server_env", test_matrix, ids=str)
def test_perf(record_property, server_env: AsgiServerEnv, num_middlewares: int):
    record_property("serie", server_env.tag)

    test_id = f"{server_env.tag}_middleware-{num_middlewares:02}"
    image = get_docker_image(server_env)
    assert image is not None, "Failed to get docker image"

    unique_dir = (
            Path(__file__).parent
            / f"../test_results/{now:%Y-%m-%dT%H%M%S}/"
    )
    unique_dir.mkdir(parents=True, exist_ok=True)

    container = docker.container.create(
        image=image,
        envs={
            "NUM_MIDDLEWARES": num_middlewares,
        },
        volumes=[(str(unique_dir), "/stats")],
    )
    print(f"starting container {container}, with {num_middlewares} middlewares")
    container.start(attach=True)

    logs = None
    for _ in range(10):
        time.sleep(1)
        logs = container.logs(timestamps=True, tail=50)
        (unique_dir / f"{test_id}_docker.log").write_text(logs)
        if "EndOfLog" in logs:
            break

    transaction_rate = extract_transaction_rate(logs)
    print(f"Transaction rate : {transaction_rate} r/s")
    assert transaction_rate is not None
    record_property("transaction_rate", transaction_rate)
