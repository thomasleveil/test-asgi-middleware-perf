import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import pytest
from _pytest.fixtures import SubRequest
from python_on_whales import DockerException, DockerClient, Image, Container

from tests.config import test_matrix, num_middlewares
from utils import plot_and_save_data, get_custom_property
from utils.docker import get_docker_image
from utils.models import AsgiServerEnv

docker = DockerClient()


@pytest.fixture(scope="session")
def results_dir(record_testsuite_property) -> Path:
    now = datetime.now()
    unique_dir = (
            Path(__file__).parent
            / f"../test_results/{now:%Y-%m-%dT%H%M%S}/"
    )
    unique_dir.mkdir(parents=True, exist_ok=True)
    record_testsuite_property("results_dir", unique_dir)
    return unique_dir


@pytest.fixture(params=test_matrix, ids=str)
def asgi_server_docker_image(request) -> tuple[AsgiServerEnv, Image]:
    """
    Pytest fixture providing a docker image for each of the configured asgi servers.
    """
    server_env = request.param
    if type(server_env) != AsgiServerEnv:
        raise TypeError(f"Expected AsgiServerEnv, got {server_env}")
    image = get_docker_image(server_env)
    assert image is not None, "Failed to get docker image"
    return server_env, image


@pytest.fixture(params=num_middlewares, ids=lambda x: f"middlewares-{x:02}")
def asgi_server(
        request: SubRequest,
        asgi_server_docker_image: tuple[AsgiServerEnv, Image],
        results_dir: Path,
) -> tuple[AsgiServerEnv, int, Container, Path]:
    """
    Pytest fixture providing a running ASGI Server to test.
    """
    server_env, docker_image = asgi_server_docker_image
    num_middlewares = request.param

    test_id = f"{server_env.tag}_middleware-{num_middlewares:02}"
    test_log_dir = (results_dir / test_id)
    test_log_dir.mkdir(parents=True, exist_ok=True)

    container = docker.container.create(
        image=docker_image,
        envs={
            "NUM_MIDDLEWARES": num_middlewares,
        },
        cpuset_cpus=[0, 1],
    )
    print(f"starting container {container}, with {num_middlewares} middlewares from image {docker_image.repo_tags}")
    container.start(attach=False)
    for _ in range(5):
        try:
            container.execute(command="/usr/bin/grep $(printf '%X\n' 80) /proc/net/tcp --count".split(" "))
        except DockerException:
            time.sleep(.5)
            continue

    yield server_env, num_middlewares, container, test_log_dir

    logs = container.logs(timestamps=True)
    print(logs)
    (results_dir / test_id / f"{request.node.originalname}_container.log").write_text(logs)

    print(f"Removing container {container}")
    container.remove(force=True)


def pytest_sessionfinish(session, exitstatus):
    series = defaultdict(lambda: (list(), list()))
    results_dir: Path
    for item in session.items:
        if item.originalname == "test_perf":
            results_dir = get_custom_property(item, "results_dir")
            serie_name = get_custom_property(item, "serie")
            num_middlewares = get_custom_property(item, "num_middlewares")
            transaction_rate = get_custom_property(item, "transaction_rate")
            series[serie_name][0].append(num_middlewares)
            series[serie_name][1].append(transaction_rate)

    plot_and_save_data(
        series=series,
        output_image_path=results_dir / 'summary.png',
        graph_title='Performances vs number of middlewares',
    )
    print(f"\nSee results in {results_dir.absolute()}")
