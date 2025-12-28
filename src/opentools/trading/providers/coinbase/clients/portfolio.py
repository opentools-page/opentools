from __future__ import annotations

from typing import Any

from .._endpoints import PORTFOLIOS_PATH
from ..transport import CoinbaseTransport


async def list_portfolios(
    transport: CoinbaseTransport,
    *,
    portfolio_type: str | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if portfolio_type is not None:
        params["portfolio_type"] = portfolio_type

    return await transport.get_dict_json(PORTFOLIOS_PATH, params=params)


async def get_portfolio_breakdown(
    transport: CoinbaseTransport,
    *,
    portfolio_uuid: str,
    currency: str | None = None,
) -> dict[str, Any]:
    params: list[str] = []

    if currency is not None:
        params.append(f"currency={currency}")

    path = f"{PORTFOLIOS_PATH}/{portfolio_uuid}"
    if params:
        path = f"{path}?{'&'.join(params)}"

    data = await transport.get_dict_json(path)
    breakdown = data.get("breakdown") or data
    return breakdown
