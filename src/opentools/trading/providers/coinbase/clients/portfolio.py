from __future__ import annotations

from typing import Any

from .._endpoints import PORTFOLIOS_PATH
from ..transport import CoinbaseTransport


async def list_portfolios(
    transport: CoinbaseTransport,
    *,
    portfolio_type: str | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] | None = None
    if portfolio_type is not None:
        params = {"portfolio_type": portfolio_type}

    return await transport.get_dict_json(PORTFOLIOS_PATH, params=params)


async def get_portfolio_breakdown(
    transport: CoinbaseTransport,
    *,
    portfolio_uuid: str,
    currency: str | None = None,
) -> dict[str, Any]:
    path = f"{PORTFOLIOS_PATH}/{portfolio_uuid}"
    params: dict[str, Any] | None = {"currency": currency} if currency else None

    data = await transport.get_dict_json(path, params=params)

    breakdown = data.get("breakdown")
    if breakdown is None:
        raise ValueError(
            f"Coinbase get_portfolio_breakdown: missing 'breakdown' key. "
            f"Keys={list(data.keys())}"
        )
    if not isinstance(breakdown, dict):
        raise TypeError(
            f"Coinbase get_portfolio_breakdown: 'breakdown' expected dict, got {type(breakdown)}"
        )

    return breakdown
