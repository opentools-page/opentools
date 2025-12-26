from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from opentools.core.transport import Transport

from ._endpoints import COINBASE_SANDBOX_URL
from .errors import raise_for_status as coinbase_raise_for_status


@dataclass
class CoinbaseTransport(Transport):
    base_url: str = COINBASE_SANDBOX_URL
    provider: str = "coinbase"
    domain: str = "trading"

    # Coinbase sometimes uses x-request-id, keep it explicit
    request_id_header_candidates: tuple[str, ...] = ("x-request-id",)

    async def get_json(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        raise_for_status: Callable | None = None,
    ) -> Any:
        return await super().get_json(
            path,
            params=params,
            raise_for_status=raise_for_status or coinbase_raise_for_status,
        )

    async def post_json(
        self,
        path: str,
        *,
        json_body: Any | None = None,
        raise_for_status: Callable | None = None,
    ) -> Any:
        return await super().post_json(
            path,
            json_body=json_body,
            raise_for_status=raise_for_status or coinbase_raise_for_status,
        )

    async def get_dict_json(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        raise_for_status: Callable | None = None,
    ) -> dict[str, Any]:
        return await super().get_dict_json(
            path,
            params=params,
            raise_for_status=raise_for_status or coinbase_raise_for_status,
        )

    async def get_list_json(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        raise_for_status: Callable | None = None,
    ) -> list[dict[str, Any]]:
        return await super().get_list_json(
            path,
            params=params,
            raise_for_status=raise_for_status or coinbase_raise_for_status,
        )
