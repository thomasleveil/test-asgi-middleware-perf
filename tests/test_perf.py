import logging
import re
import time
from datetime import datetime
from pathlib import Path

import pytest
from python_on_whales import DockerClient

####################################################
num_queries = 1_000
num_middleware = range(25)
test_matrix = [
    {
        "python": "3.12.1",
        "starlette": "0.34.0",
        "uvicorn": "0.25.0",
    },
    # {
    #     "python": "3.13.0a2",
    #     "starlette": "0.34.0",
    #     "uvicorn": "0.25.0",
    # },
]

####################################################

now = datetime.now()
dockerfile = Path(__file__).parent / "../docker/Dockerfile"
docker = DockerClient()

docker_images_cache = {}


def build_image(context_path, python_version, starlette_version, uvicorn_version):
    key = f"p{python_version}-u{uvicorn_version}-s{starlette_version}"
    if key in docker_images_cache:
        return docker_images_cache[key]
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
        tags=[f"test-starlette-perf:p{python_version}-u{uvicorn_version}-s{starlette_version}"],
    )
    docker_images_cache[key] = image
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
@pytest.mark.parametrize("versions", test_matrix, ids=str)
def test_perf(record_property, extras, versions, num_middleware):
    python_version = versions["python"]
    starlette_version = versions["starlette"]
    uvicorn_version = versions["uvicorn"]
    test_id = f"s{starlette_version}_p{python_version}_u{uvicorn_version}_middleware-{num_middleware:02}"

    image = build_image(
        dockerfile.parent,
        python_version=python_version,
        starlette_version=starlette_version,
        uvicorn_version=uvicorn_version,
    )
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

    time.sleep(2)
    logs = container.logs(timestamps=True, tail=19)
    (unique_dir / f"{test_id}_docker.log").write_text(logs)

    transaction_rate = extract_transaction_rate(logs)
    print(f"Transaction rate : {transaction_rate} r/s")
    record_property("transaction_rate", transaction_rate)
