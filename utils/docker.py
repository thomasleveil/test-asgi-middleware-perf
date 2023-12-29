import logging
from dataclasses import fields
from pathlib import Path
from typing import Type

from python_on_whales import Image, DockerClient

from utils.models import ServerEnv

docker = DockerClient()
docker_images_cache = {}


def build_docker_image(server_env: Type[ServerEnv]) -> Image:
    context_path = Path(__file__).parent / f"../docker/{server_env.name}"
    if not context_path.is_dir():
        raise ValueError(f"expecting {context_path} to be a directory")
    if not (context_path / "Dockerfile").is_file():
        raise ValueError(f"expecting {context_path} to contain Dockerfile")

    tag = f"test-asgi-perf:{server_env.key}"
    if tag in docker_images_cache:
        return docker_images_cache[tag]
    logging.info(
        f"building image for {server_env}")
    image = docker.buildx.build(
        context_path=context_path,
        build_args={
            f"{field.name.upper()}_VERSION": getattr(server_env, field.name)
            for field in fields(server_env)
        },
        cache=True,
        progress="plain",
        load=True,
        tags=[tag],
    )
    docker_images_cache[tag] = image
    return image
