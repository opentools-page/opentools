from __future__ import annotations

from typing import Any

from .._endpoints import ORDER_HISTORICAL_PATH, ORDERS_HISTORICAL_PATH
from ..transport import CoinbaseTransport


async def list_orders(
    transport: CoinbaseTransport,
    *,
    limit: int | None = None,
    cursor: str | None = None,
    product_ids: list[str] | None = None,
    order_status: str | None = None,
    order_side: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    if limit is not None:
        params["limit"] = limit

    if cursor is not None:
        params["cursor"] = cursor

    if product_ids:
        params["product_ids"] = product_ids

    if order_status:
        # Coinbase expects a list of statuses
        params["order_status"] = [order_status]

    if order_side:
        params["order_side"] = order_side

    if start_date:
        params["start_date"] = start_date

    if end_date:
        params["end_date"] = end_date

    return await transport.get_dict_json(ORDERS_HISTORICAL_PATH, params=params)


async def get_order(
    transport: CoinbaseTransport,
    order_id: str,
) -> dict[str, Any]:
    path = ORDER_HISTORICAL_PATH.format(order_id=order_id)
    return await transport.get_dict_json(path)
