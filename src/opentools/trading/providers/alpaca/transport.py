from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from opentools.auth.interfaces import Auth
from opentools.core.errors import AuthError, ProviderError, TransientError

from ._endpoints import PAPER_BASE_URL
from .errors import raise_for_status


@dataclass
class AlpacaTransport:
    """
    Layer 1 (HTTP transport) for Alpaca.

    Responsibilities:
      - ask auth for request headers
      - make HTTP requests
      - translate HTTP status codes into canonical OpenTools errors
      - return parsed JSON (dict or list)
    """

    auth: Auth
    base_url: str = PAPER_BASE_URL
    timeout: float = 30.0
    provider: str = "alpaca"
    domain: str = "trading"

    async def _headers(self) -> dict[str, str]:
        try:
            h = await self.auth.headers()
            headers = dict(h)
        except Exception as e:
            raise AuthError(
                message="Failed to build auth headers",
                domain=self.domain,
                provider=self.provider,
                details=repr(e),
            )

        headers.setdefault("Accept", "application/json")
        return headers

    async def get_json(self, path: str) -> Any:
        url = f"{self.base_url}{path}"
        headers = await self._headers()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.get(url, headers=headers)
        except httpx.TimeoutException as e:
            raise TransientError(
                message="Request timed out",
                domain=self.domain,
                provider=self.provider,
                details=repr(e),
            )
        except httpx.RequestError as e:
            raise TransientError(
                message="Network error",
                domain=self.domain,
                provider=self.provider,
                details=repr(e),
            )

        request_id = r.headers.get("x-request-id") or r.headers.get(
            "x-alpaca-request-id"
        )

        retry_after_s: float | None = None
        ra = r.headers.get("retry-after")
        if ra:
            try:
                retry_after_s = float(ra)
            except ValueError:
                retry_after_s = None

        if r.status_code >= 400:
            raise_for_status(
                status_code=r.status_code,
                text=r.text,
                domain=self.domain,
                provider=self.provider,
                request_id=request_id,
                retry_after_s=retry_after_s,
            )

        try:
            return r.json()
        except ValueError as e:
            raise ProviderError(
                message="Provider returned invalid JSON",
                domain=self.domain,
                provider=self.provider,
                status_code=r.status_code,
                request_id=request_id,
                details={"error": repr(e), "text": r.text},
            )

    async def get_dict_json(self, path: str) -> dict[str, Any]:
        """
        GET and assert response is a dict.
        """
        data = await self.get_json(path)
        if not isinstance(data, dict):
            raise ProviderError(
                message="Expected dict JSON response",
                domain=self.domain,
                provider=self.provider,
                details={"type": type(data).__name__, "data": data},
            )
        return data

    async def get_list_json(self, path: str) -> list[dict[str, Any]]:
        data = await self.get_json(path)
        if not isinstance(data, list):
            raise ProviderError(
                message="Expected list JSON response",
                domain=self.domain,
                provider=self.provider,
                details={"type": type(data).__name__, "data": data},
            )

        out: list[dict[str, Any]] = []
        for item in data:
            if isinstance(item, dict):
                out.append(item)
            else:
                raise ProviderError(
                    message="Expected list of objects in JSON response",
                    domain=self.domain,
                    provider=self.provider,
                    details={"item_type": type(item).__name__, "item": item},
                )
        return out
