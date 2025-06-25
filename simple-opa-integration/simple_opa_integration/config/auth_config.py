from dataclasses import dataclass


@dataclass(repr=True, frozen=True)
class AuthConfig:
    host: str
    port: int
    uri: str

    @property
    def url(self) -> str:
        uri = self.uri.lstrip("/")
        return f"http://{self.host}:{self.port}/{uri}"

