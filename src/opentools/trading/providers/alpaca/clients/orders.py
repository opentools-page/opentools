from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from .._endpoints import ORDER_PATH, ORDERS_PATH
from ..transport import AlpacaTransport


async def list_orders(
    transport: AlpacaTransport,
    *,
    status: str | None = None,
    limit: int | None = None,
    after: str | None = None,
    until: str | None = None,
    direction: str | None = None,
    nested: bool | None = None,
    symbols: list[str] | None = None,
    side: str | None = None,
    asset_class: list[str] | None = None,
    before_order_id: str | None = None,
    after_order_id: str | None = None,
) -> list[dict[str, Any]]:
    params: dict[str, str] = {}

    if status is not None:
        params["status"] = status
    if limit is not None:
        # Alpaca max is 500
        params["limit"] = str(min(limit, 500))
    if after is not None:
        params["after"] = after
    if until is not None:
        params["until"] = until
    if direction is not None:
        params["direction"] = direction
    if nested is not None:
        params["nested"] = "true" if nested else "false"
    if symbols:
        params["symbols"] = ",".join(symbols)
    if side is not None:
        params["side"] = side
    if asset_class:
        params["asset_class"] = ",".join(asset_class)
    if before_order_id is not None:
        params["before_order_id"] = before_order_id
    if after_order_id is not None:
        params["after_order_id"] = after_order_id

    query = f"?{urlencode(params)}" if params else ""

    return await transport.get_list_json(ORDERS_PATH + query)


async def get_order(
    transport: AlpacaTransport,
    order_id: str,
    *,
    nested: bool | None = None,
) -> dict[str, Any]:
    path = ORDER_PATH.format(order_id=order_id)

    params: dict[str, str] = {}
    if nested is not None:
        params["nested"] = "true" if nested else "false"

    query = f"?{urlencode(params)}" if params else ""

    return await transport.get_dict_json(path + query)
