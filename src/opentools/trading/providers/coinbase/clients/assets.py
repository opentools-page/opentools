from __future__ import annotations

from typing import Any

from .._endpoints import PRODUCT_PATH, PRODUCTS_PATH
from ..transport import CoinbaseTransport


async def list_assets(
    transport: CoinbaseTransport,
    *,
    status: str | None = None,  # unused
    asset_class: str | None = None,  # product type
    exchange: str | None = None,  # unused
    attributes: list[str] | None = None,
    limit: int | None = None,
    cursor: str | None = None,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {}

    if limit is not None:
        params["limit"] = limit

    if cursor is not None:
        params["cursor"] = cursor

    if asset_class is not None:
        normalized = asset_class.lower()
        if normalized in ("spot", "crypto"):
            params["product_type"] = "SPOT"
        elif normalized in ("future", "futures"):
            params["product_type"] = "FUTURE"
        else:
            params["product_type"] = asset_class

    if attributes:
        if "tradable" in attributes:
            params["get_tradability_status"] = True
        if "all" in attributes:
            params["get_all_products"] = True

    data = await transport.get_dict_json(PRODUCTS_PATH, params=params)
    products = data.get("products") or []
    return products


async def get_asset(
    transport: CoinbaseTransport,
    product_id: str,
    *,
    get_tradability_status: bool | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    if get_tradability_status is not None:
        params["get_tradability_status"] = get_tradability_status

    path = PRODUCT_PATH.format(product_id=product_id)
    data = await transport.get_dict_json(path, params=params)
    return data
