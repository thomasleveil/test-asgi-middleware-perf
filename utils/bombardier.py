from python_on_whales import Container, DockerClient

from utils.docker import build_docker_bombardier_image

docker = DockerClient()


def run_bombardier(url: str) -> str:
    bombardier_image = build_docker_bombardier_image()

    container = docker.container.create(
        image=bombardier_image,
        cpuset_cpus=[2, 3],
        command=f"/bombardier --duration=20s --format=json {url}".split(" ")
    )
    print(f"starting bombardier container {container}")
    try:
        container.start(attach=True)
        logs = container.logs(timestamps=False)
        print(logs)
        container.remove(force=True)
        return logs
    finally:
        print(f"Removing bomboardier container {container}")
        container.remove(force=True)
