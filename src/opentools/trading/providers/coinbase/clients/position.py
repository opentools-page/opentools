from __future__ import annotations

from typing import Any

from ..transport import CoinbaseTransport
from .portfolio import (
    get_portfolio_breakdown as _get_portfolio_breakdown,
)
from .portfolio import (
    list_portfolios as _list_portfolios,
)


async def _resolve_default_portfolio_uuid(
    transport: CoinbaseTransport,
    *,
    portfolio_type: str | None = None,
) -> str | None:
    portfolios: list[dict[str, Any]] = []

    if portfolio_type:
        # explicit type (DEFAULT / CONSUMER / INTX / UNDEFINED)
        resp = await _list_portfolios(
            transport,
            portfolio_type=portfolio_type,
        )
        portfolios = resp.get("portfolios") or []
    else:
        for pt in ("DEFAULT", "UNDEFINED"):
            resp = await _list_portfolios(
                transport,
                portfolio_type=pt,
            )
            portfolios = resp.get("portfolios") or []
            if portfolios:
                break

    if not isinstance(portfolios, list) or not portfolios:
        return None

    first = portfolios[0] or {}
    uuid = first.get("uuid")
    if not isinstance(uuid, str):
        return None

    return uuid


async def list_positions(
    transport: CoinbaseTransport,
    *,
    portfolio_type: str | None = None,
    currency: str | None = None,
) -> list[dict[str, Any]]:
    portfolio_uuid = await _resolve_default_portfolio_uuid(
        transport,
        portfolio_type=portfolio_type,
    )
    if not portfolio_uuid:
        return []

    breakdown = await _get_portfolio_breakdown(
        transport,
        portfolio_uuid=portfolio_uuid,
        currency=currency,
    )

    if not isinstance(breakdown, dict):
        return []

    positions: list[dict[str, Any]] = []

    # Spot positions (cash / crypto balances)
    for item in breakdown.get("spot_positions") or []:
        row = dict(item)
        row["_opentools_position_kind"] = "spot"
        positions.append(row)

    # Perpetual futures
    for item in breakdown.get("perp_positions") or []:
        row = dict(item)
        row["_opentools_position_kind"] = "perp"
        positions.append(row)

    # Dated futures
    for item in breakdown.get("futures_positions") or []:
        row = dict(item)
        row["_opentools_position_kind"] = "future"
        positions.append(row)

    return positions
