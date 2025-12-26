from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

import httpx

from opentools.auth.interface import Auth
from opentools.core.errors import AuthError, ProviderError, TransientError


@dataclass
class Transport:
    auth: Auth
    base_url: str
    timeout: float = 30.0
    provider: str = "unknown"
    domain: str = "trading"

    request_id_header_candidates: tuple[str, ...] = ("x-request-id",)

    async def _headers(self, *, method: str, path: str) -> dict[str, str]:
        try:
            h: Mapping[str, str] = await self.auth.headers(method=method, path=path)
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

    def _extract_request_id(self, r: httpx.Response) -> str | None:
        for key in self.request_id_header_candidates:
            val = r.headers.get(key)
            if val:
                return val
        return None

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any | None = None,
        raise_for_status: Callable | None = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        headers = await self._headers(method=method, path=path)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                r = await client.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    json=json_body,
                )
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

        request_id = self._extract_request_id(r)

        retry_after_s: float | None = None
        ra = r.headers.get("retry-after")
        if ra:
            try:
                retry_after_s = float(ra)
            except ValueError:
                retry_after_s = None

        if r.status_code >= 400 and raise_for_status is not None:
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

    async def get_json(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        raise_for_status: Callable | None = None,
    ) -> Any:
        return await self._request(
            "GET",
            path,
            params=params,
            raise_for_status=raise_for_status,
        )

    async def post_json(
        self,
        path: str,
        *,
        json_body: Any | None = None,
        raise_for_status: Callable | None = None,
    ) -> Any:
        return await self._request(
            "POST",
            path,
            json_body=json_body,
            raise_for_status=raise_for_status,
        )

    async def get_dict_json(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        raise_for_status: Callable | None = None,
    ) -> dict[str, Any]:
        data = await self.get_json(
            path,
            params=params,
            raise_for_status=raise_for_status,
        )
        if not isinstance(data, dict):
            raise ProviderError(
                message="Expected dict JSON response",
                domain=self.domain,
                provider=self.provider,
                details={"type": type(data).__name__, "data": data},
            )
        return data

    async def get_list_json(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        raise_for_status: Callable | None = None,
    ) -> list[dict[str, Any]]:
        data = await self.get_json(
            path,
            params=params,
            raise_for_status=raise_for_status,
        )
        if not isinstance(data, list):
            raise ProviderError(
                message="Expected list of objects in JSON response",
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
