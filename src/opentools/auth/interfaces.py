from typing import Mapping, Protocol


class Auth(Protocol):
    async def headers(self) -> Mapping[str, str]: ...
