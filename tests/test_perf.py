import time
from datetime import datetime
from pathlib import Path
from typing import Type

import pytest
from python_on_whales import DockerClient

from utils import extract_transaction_rate
from utils.docker import build_docker_image
from utils.models import ServerEnv, StarletteServerEnv, LitestarServerEnv, BlacksheepServerEnv, SanicServerEnv, \
    MuffinServerEnv, FalconServerEnv, FastapiServerEnv

####################################################
num_queries = 5_000
num_middleware = range(9)
test_matrix: list[ServerEnv] = [
    StarletteServerEnv(
        python="3.12.1",
        uvicorn="0.25.0",
        starlette="0.34.0",
    ),
    # StarletteServerEnv(
    #     python="3.13.0a2",
    #     uvicorn="0.25.0",
    #     starlette="0.34.0",
    # ),
    BlacksheepServerEnv(
        python="3.12.1",
        uvicorn="0.25.0",
        blacksheep="2.0.3",
    ),
    FalconServerEnv(
        python="3.12.1",
        uvicorn="0.25.0",
        falcon="3.1.3",
    ),
    FastapiServerEnv(
        python="3.12.1",
        uvicorn="0.25.0",
        fastapi="0.108.0",
    ),
    LitestarServerEnv(
        python="3.12.1",
        uvicorn="0.25.0",
        litestar="2.4.5",
    ),
    MuffinServerEnv(
        python="3.12.1",
        uvicorn="0.25.0",
        muffin="0.100.1",
    ),
    SanicServerEnv(
        python="3.12.1",
        uvicorn="0.25.0",
        sanic="23.6.0",
    ),
]
####################################################

now = datetime.now()
docker = DockerClient()


@pytest.mark.flaky(max_runs=4)
@pytest.mark.parametrize(
    "num_middleware", num_middleware, ids=lambda x: f"middlewares-{x:02}"
)
@pytest.mark.parametrize("server_env", test_matrix, ids=str)
def test_perf(record_property, server_env: Type[ServerEnv], num_middleware: int):
    record_property("serie", server_env.key)

    test_id = f"{server_env.key}_middleware-{num_middleware:02}"
    image = build_docker_image(server_env)
    assert image is not None, "Failed to build docker image"

    unique_dir = (
            Path(__file__).parent
            / f"../test_results/{now:%Y-%m-%dT%H%M%S}/"
    )
    unique_dir.mkdir(parents=True, exist_ok=True)

    container = docker.container.create(
        image=image,
        command=[str(num_middleware), str(num_queries)],
        volumes=[(str(unique_dir), "/stats")],
        labels={
            "num_middlewares": num_middleware,
        },
    )
    print(f"starting container {container}, with {num_middleware} middlewares")
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
