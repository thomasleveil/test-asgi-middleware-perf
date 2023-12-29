import logging
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pytest
from python_on_whales import DockerClient, Image

now = datetime.now()
docker = DockerClient()

docker_images_cache = {}


@dataclass
class ServerEnv:
    python: str
    uvicorn: str

    @property
    def key(self) -> str:
        raise NotImplementedError()

    def get_docker_image(self) -> Image:
        raise NotImplementedError()


@dataclass
class StarletteServerEnv(ServerEnv):
    starlette: str

    @property
    def key(self) -> str:
        return f"starlette_{self.starlette}_p{self.python}_u{self.uvicorn}"

    def get_docker_image(self):
        image = build_starlette_image(
            Path(__file__).parent / "../docker-starlette",
            python_version=self.python,
            starlette_version=self.starlette,
            uvicorn_version=self.uvicorn,
        )
        return image


@dataclass
class LitestarServerEnv(ServerEnv):
    litestar: str

    @property
    def key(self) -> str:
        return f"litestar_{self.litestar}_p{self.python}_u{self.uvicorn}"

    def get_docker_image(self):
        image = build_litestar_image(
            Path(__file__).parent / "../docker-litestar",
            python_version=self.python,
            litestar_version=self.litestar,
            uvicorn_version=self.uvicorn,
        )
        return image


####################################################
num_queries = 1_000
num_middleware =  range(5)
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
    LitestarServerEnv(
        python="3.12.1",
        uvicorn="0.25.0",
        litestar="2.4.5",
    ),
]


####################################################


def build_starlette_image(context_path, python_version, starlette_version, uvicorn_version) -> Image:
    tag = f"test-starlette-perf:p{python_version}-u{uvicorn_version}-s{starlette_version}"
    if tag in docker_images_cache:
        return docker_images_cache[tag]
    logging.info(
        f"building image for Starlette {starlette_version} with Python {python_version} and Uvicorn {uvicorn_version}")
    image = docker.buildx.build(
        context_path=context_path,
        build_args={
            "PYTHON_VERSION": python_version,
            "STARLETTE_VERSION": starlette_version,
            "UVICORN_VERSION": uvicorn_version,
        },
        cache=True,
        progress="plain",
        load=True,
        tags=[tag],
    )
    docker_images_cache[tag] = image
    return image


def build_litestar_image(context_path, python_version, litestar_version, uvicorn_version) -> Image:
    tag = f"test-litestar-perf:p{python_version}-u{uvicorn_version}-l{litestar_version}"
    if tag in docker_images_cache:
        return docker_images_cache[tag]
    logging.info(
        f"building image for Litestar {litestar_version} with Python {python_version} and Uvicorn {uvicorn_version}")
    image = docker.buildx.build(
        context_path=context_path,
        build_args={
            "PYTHON_VERSION": python_version,
            "LITESTAR_VERSION": litestar_version,
            "UVICORN_VERSION": uvicorn_version,
        },
        cache=True,
        progress="plain",
        load=True,
        tags=[tag],
    )
    docker_images_cache[tag] = image
    return image


def extract_transaction_rate(raw_text):
    """
    Extracts the transaction rate from the provided raw text.

    Args:
    raw_text (str): A string containing the raw text from which the transaction rate needs to be extracted.

    Returns:
    float: The extracted transaction rate, or None if it's not found.
    """
    # Regular expression to find the transaction rate in the text
    transaction_rate_pattern = r'"transaction_rate":\s*([0-9.]+)'

    # Search for the transaction rate in the text
    match = re.search(transaction_rate_pattern, raw_text)

    # If a match is found, return the transaction rate as a float, otherwise return None
    if match:
        return float(match.group(1))
    else:
        return None


@pytest.mark.parametrize(
    "num_middleware", num_middleware, ids=lambda x: f"middlewares-{x:02}"
)
@pytest.mark.parametrize("server_env", test_matrix, ids=str)
def test_perf(record_property, server_env, num_middleware: int):
    record_property("serie", server_env.key)
    test_id = f"{server_env.key}_middleware-{num_middleware:02}"
    image = server_env.get_docker_image()
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

    for _ in range(10):
        time.sleep(1)
        logs = container.logs(timestamps=True, tail=50)
        (unique_dir / f"{test_id}_docker.log").write_text(logs)
        if "EndOfLog" in logs:
            break

    transaction_rate = extract_transaction_rate(logs)
    print(f"Transaction rate : {transaction_rate} r/s")
    record_property("transaction_rate", transaction_rate)
    assert transaction_rate is not None
