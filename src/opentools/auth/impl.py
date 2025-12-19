from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class BearerTokenAuth:
    token: str

    async def headers(self) -> Mapping[str, str]:
        return {"Authorization": f"Bearer {self.token}"}


@dataclass(frozen=True)
class HeaderAuth:
    headers_dict: Mapping[str, str]

    async def headers(self) -> Mapping[str, str]:
        return dict(self.headers_dict)


@dataclass(frozen=True)
class AlpacaAuth:
    key_id: str
    secret_key: str

    async def headers(self) -> Mapping[str, str]:
        return {
            "APCA-API-KEY-ID": self.key_id,
            "APCA-API-SECRET-KEY": self.secret_key,
        }
