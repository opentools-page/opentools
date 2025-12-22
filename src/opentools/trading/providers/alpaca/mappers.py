from __future__ import annotations

from datetime import datetime
from typing import Any

from ...schemas import Account, Clock, Position


def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def account_from_alpaca(data: dict[str, Any]) -> Account:
    return Account(
        id=data.get("id"),
        status=data.get("status"),
        currency=data.get("currency"),
        cash=data.get("cash"),
        buying_power=data.get("buying_power"),
        equity=data.get("equity"),
        portfolio_value=data.get("portfolio_value"),
        created_at=_parse_dt(data.get("created_at")),
        provider="alpaca",
        provider_fields=dict(data),
    )


def position_from_alpaca(data: dict[str, Any]) -> Position | None:
    symbol = data.get("symbol")
    if not symbol:
        return None

    return Position(
        symbol=symbol,
        qty=data.get("qty"),
        avg_entry_price=data.get("avg_entry_price"),
        current_price=data.get("current_price"),
        market_value=data.get("market_value"),
        unrealized_pl=data.get("unrealized_pl"),
        unrealized_plpc=data.get("unrealized_plpc"),
        side=data.get("side"),
        provider="alpaca",
        provider_fields=dict(data),
    )


def clock_from_alpaca(data: dict[str, Any]) -> Clock:
    return Clock(
        timestamp=_parse_dt(data.get("timestamp")),
        is_open=data.get("is_open"),
        next_open=_parse_dt(data.get("next_open")),
        next_close=_parse_dt(data.get("next_close")),
        provider="alpaca",
        provider_fields=dict(data),
    )
