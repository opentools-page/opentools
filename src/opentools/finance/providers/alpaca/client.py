from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from opentools.auth.interfaces import Auth
from opentools.core.errors import AuthError, ProviderError, TransientError

from ._endpoints import ACCOUNT_PATH, PAPER_BASE_URL, POSITIONS_PATH
from .errors import raise_for_status


@dataclass
class AlpacaClient:
    auth: Auth
    base_url: str = PAPER_BASE_URL
    timeout_s: float = 30.0

    provider: str = "alpaca"

    async def _headers(self) -> dict[str, str]:
        try:
            h = await self.auth.headers()
            return {**dict(h), "Accept": "application/json"}
        except Exception as e:
            raise AuthError(
                message="Failed to build auth headers",
                domain="finance",
                provider=self.provider,
                details=repr(e),
            )

    async def _get_json(self, path: str) -> Any:
        url = f"{self.base_url}{path}"
        headers = await self._headers()

        try:
            async with httpx.AsyncClient(timeout=self.timeout_s) as client:
                r = await client.get(url, headers=headers)
        except httpx.TimeoutException as e:
            raise TransientError(
                message="Request timed out",
                domain="finance",
                provider=self.provider,
                details=repr(e),
            )
        except httpx.RequestError as e:
            raise TransientError(
                message="Network error",
                domain="finance",
                provider=self.provider,
                details=repr(e),
            )

        request_id = r.headers.get("x-request-id") or r.headers.get(
            "x-alpaca-request-id"
        )

        if r.status_code >= 400:
            raise_for_status(
                status_code=r.status_code,
                text=r.text,
                domain="finance",
                provider=self.provider,
                request_id=request_id,
            )

        return r.json()

    async def get_account(self) -> dict:
        return await self._get_json(ACCOUNT_PATH)

    async def list_positions(self) -> list[dict]:
        data = await self._get_json(POSITIONS_PATH)
        if not isinstance(data, list):
            raise ProviderError(
                message="Expected list response for positions",
                domain="finance",
                provider=self.provider,
                details={"type": type(data).__name__, "data": data},
            )
        return data

    async def get_quote(self, symbol: str) -> dict:
        raise NotImplementedError("get_quote not implemented yet")

    async def place_order(self, payload: dict) -> dict:
        raise NotImplementedError("place_order not implemented yet")
