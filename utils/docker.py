import logging
from pathlib import Path

from python_on_whales import Image, DockerClient
from python_on_whales.exceptions import NoSuchImage

from utils.models import AsgiServerEnv

docker = DockerClient()
docker_images_cache = {}


def build_docker_base_image(server_env: AsgiServerEnv) -> Image:
    context_path = Path(__file__).parent / f"../docker/baseimage"
    if not context_path.is_dir():
        raise ValueError(f"expecting {context_path} to be a directory")
    if not (context_path / "Dockerfile").is_file():
        raise ValueError(f"expecting {context_path} to contain Dockerfile")

    tag = f"test-asgi-perf:baseimage-{server_env.base_image_tag}"
    if tag in docker_images_cache:
        return docker_images_cache[tag]
    logging.info(
        f"building base image for {server_env.base_image_tag}")
    image = docker.buildx.build(
        context_path=context_path,
        build_args={
            "PYTHON_VERSION": server_env.python,
            "UVICORN_VERSION": server_env.uvicorn,
            "GUNICORN_VERSION": server_env.gunicorn,
        },
        cache=True,
        progress="plain",
        load=True,
        tags=[tag],
    )
    docker_images_cache[tag] = image
    return image


def build_docker_image(server_env: AsgiServerEnv) -> Image:
    server_script_path = Path(__file__).parent / f"../docker/{server_env.asgi_module}_server.py"
    if not server_script_path.is_file():
        raise ValueError(f"expecting {server_script_path}")

    tag = f"test-asgi-perf:{server_env.tag}"
    if tag in docker_images_cache:
        return docker_images_cache[tag]

    logging.info(f"building image for {server_env}")
    baseimage = build_docker_base_image(server_env)

    image = docker.buildx.build(
        context_path=Path(__file__).parent / '../docker/',
        build_args={
            "BASEIMAGE": baseimage.repo_tags[0],
            "ASGI_MODULE": server_env.asgi_module,
            "ASGI_VERSION": server_env.asgi_version,
        },
        cache=True,
        progress="plain",
        load=True,
        tags=[tag],
    )
    docker_images_cache[tag] = image
    return image


def get_docker_image(server_env: AsgiServerEnv) -> Image:
    try:
        return docker.image.inspect(f"test-asgi-perf:{server_env.tag}")
    except NoSuchImage:
        return build_docker_image(server_env)


if __name__ == "__main__":
    server_env = AsgiServerEnv(
        asgi_module="starlette",
        asgi_version="0.34.0",
        python="3.12.1",
        uvicorn="0.25.0",
        gunicorn="21.2.0",
    )
    print(server_env.base_image_tag)
    baseimage = build_docker_base_image(server_env)
    print(baseimage.repo_tags)

    print(server_env.tag)
    build_docker_image(server_env)
