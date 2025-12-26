from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .coinbase_jwt import build_coinbase_jwt


@dataclass(frozen=True)
class BearerTokenAuth:
    token: str

    async def headers(
        self,
        *,
        method: str | None = None,
        path: str | None = None,
    ) -> Mapping[str, str]:
        _ = method, path
        return {"Authorization": f"Bearer {self.token}"}


@dataclass(frozen=True)
class HeaderAuth:
    headers_dict: Mapping[str, str]

    async def headers(
        self,
        *,
        method: str | None = None,
        path: str | None = None,
    ) -> Mapping[str, str]:
        _ = method, path
        return dict(self.headers_dict)


@dataclass(frozen=True)
class AlpacaAuth:
    key_id: str
    secret_key: str

    async def headers(
        self,
        *,
        method: str | None = None,
        path: str | None = None,
    ) -> Mapping[str, str]:
        _ = method, path
        return {
            "APCA-API-KEY-ID": self.key_id,
            "APCA-API-SECRET-KEY": self.secret_key,
        }


@dataclass(frozen=True)
class CoinbaseAuth:
    api_key: str
    api_secret: str
    host: str
    expires_in: int = 120

    async def headers(
        self,
        *,
        method: str | None = None,
        path: str | None = None,
    ) -> Mapping[str, str]:
        if method is None or path is None:
            raise ValueError("CoinbaseAuth.headers requires method and path")

        token = build_coinbase_jwt(
            key_name=self.api_key,
            key_secret=self.api_secret,
            method=method,
            host=self.host,
            path=path,
            expires_in=self.expires_in,
        )
        return {"Authorization": f"Bearer {token}"}
