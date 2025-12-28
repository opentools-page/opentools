from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from opentools.core.errors import AuthError
from opentools.core.transport import Transport

from ._endpoints import ALPACA_PAPER_URL
from .errors import raise_for_status as alpaca_raise_for_status


@dataclass
class AlpacaTransport(Transport):
    base_url: str = ALPACA_PAPER_URL
    provider: str = "alpaca"
    domain: str = "trading"
    environment: str | None = None

    request_id_header_candidates: tuple[str, ...] = (
        "x-alpaca-request-id",
        "x-request-id",
    )

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
            raise_for_status=raise_for_status or alpaca_raise_for_status,
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
            raise_for_status=raise_for_status or alpaca_raise_for_status,
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
                raise_for_status=raise_for_status or alpaca_raise_for_status,
            )
        except AuthError as e:
            env = self.environment or "unknown"
            msg = f"{e.message} (Alpaca environment={env}, base_url={self.base_url})"

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
            raise_for_status=raise_for_status or alpaca_raise_for_status,
        )
