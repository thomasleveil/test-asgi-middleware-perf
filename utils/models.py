from dataclasses import dataclass


@dataclass
class ServerEnv:
    python: str
    uvicorn: str
    gunicorn: str

    @property
    def base_image_tag(self) -> str:
        return f"p{self.python}_g{self.gunicorn}_u{self.uvicorn}"


@dataclass
class AsgiServerEnv(ServerEnv):
    asgi_module: str
    asgi_version: str

    @property
    def tag(self) -> str:
        return f"{self.asgi_module}_{self.asgi_version}__{self.base_image_tag}"

    def __str__(self) -> str:
        return f"{self.asgi_module} {self.asgi_version}, {self.base_image_tag}"