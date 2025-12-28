from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from opentools.core.errors import AuthError
from opentools.core.transport import Transport

from ._endpoints import COINBASE_LIVE_URL
from .errors import raise_for_status as coinbase_raise_for_status


@dataclass
class CoinbaseTransport(Transport):
    base_url: str = COINBASE_LIVE_URL
    provider: str = "coinbase"
    domain: str = "trading"

    # "live" / "paper"
    environment: str | None = None

    # explicit
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
        try:
            data = await super().get_dict_json(
                path,
                params=params,
                raise_for_status=raise_for_status or coinbase_raise_for_status,
            )
        except AuthError as e:
            env = (
                f"environment={self.environment}"
                if self.environment
                else "environment=unknown"
            )
            msg = f"{e.message} (Coinbase {env}, base_url={self.base_url})"

            raise AuthError(
                message=msg,
                domain=e.domain,
                provider=e.provider,
                status_code=e.status_code,
                request_id=getattr(e, "request_id", None),
                details=e.details,
            ) from e

        return data

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
