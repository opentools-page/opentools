from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from .._endpoints import ASSET_PATH, ASSETS_PATH
from ..transport import AlpacaTransport


async def list_assets(
    transport: AlpacaTransport,
    *,
    status: str | None = None,
    asset_class: str | None = None,
    exchange: str | None = None,
    attributes: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    GET /v2/assets with optional Alpaca-style filters.
    """
    params: dict[str, str] = {}

    if status is not None:
        params["status"] = status
    if asset_class is not None:
        params["asset_class"] = asset_class
    if exchange is not None:
        params["exchange"] = exchange
    if attributes:
        params["attributes"] = ",".join(attributes)

    query = f"?{urlencode(params)}" if params else ""

    return await transport.get_list_json(ASSETS_PATH + query)


async def get_asset(
    transport: AlpacaTransport,
    symbol_or_asset_id: str,
) -> dict[str, Any]:
    """
    GET /v2/assets/{symbol_or_asset_id}
    """
    path = ASSET_PATH.format(symbol_or_asset_id=symbol_or_asset_id)
    return await transport.get_dict_json(path)
