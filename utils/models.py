from dataclasses import dataclass, fields


@dataclass
class ServerEnv:
    python: str
    uvicorn: str

    @property
    def name(self) -> str:
        return self.__class__.__name__.replace("ServerEnv", "").lower()

    @property
    def key(self) -> str:
        versions = {
            field.name: getattr(self, field.name)
            for field in fields(self)
        }
        version_parts = [
            f"u{versions.pop('uvicorn')}",
            f"p{versions.pop('python')}"
        ]
        version_parts.extend([
            f"{k[0]}{v}"
            for k, v in versions.items()
        ])
        return f"{self.name}_{'_'.join(reversed(version_parts))}"


@dataclass
class BlacksheepServerEnv(ServerEnv):
    blacksheep: str


@dataclass
class FalconServerEnv(ServerEnv):
    falcon: str


@dataclass
class LitestarServerEnv(ServerEnv):
    litestar: str


@dataclass
class MuffinServerEnv(ServerEnv):
    muffin: str


@dataclass
class SanicServerEnv(ServerEnv):
    sanic: str


@dataclass
class StarletteServerEnv(ServerEnv):
    starlette: str
