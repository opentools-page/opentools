from __future__ import annotations

from typing import Mapping, Protocol


class Auth(Protocol):
    async def headers(
        self,
        *,
        method: str | None = None,
        path: str | None = None,
    ) -> Mapping[str, str]: ...
