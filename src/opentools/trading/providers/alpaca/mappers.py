from __future__ import annotations

from datetime import datetime
from typing import Any

from ...schemas import Account, Asset, Clock, Order, Position


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


def asset_from_alpaca(data: dict[str, Any]) -> Asset | None:
    symbol = data.get("symbol")
    if not symbol:
        return None

    return Asset(
        id=data.get("id"),
        symbol=symbol,
        name=data.get("name"),
        exchange=data.get("exchange"),
        asset_class=data.get("asset_class"),
        status=data.get("status"),
        tradable=data.get("tradable"),
        marginable=data.get("marginable"),
        shortable=data.get("shortable"),
        easy_to_borrow=data.get("easy_to_borrow"),
        fractionable=data.get("fractionable"),
        provider="alpaca",
        provider_fields=dict(data),
    )


def order_from_alpaca(data: dict[str, Any]) -> Order | None:
    order_id = data.get("id")
    if not order_id:
        return None

    return Order(
        provider="alpaca",
        id=order_id,
        client_order_id=data.get("client_order_id"),
        symbol=data.get("symbol"),
        side=data.get("side"),
        type=data.get("type"),
        time_in_force=data.get("time_in_force"),
        status=data.get("status"),
        qty=data.get("qty"),
        notional=data.get("notional"),
        filled_qty=data.get("filled_qty"),
        filled_avg_price=data.get("filled_avg_price"),
        limit_price=data.get("limit_price"),
        stop_price=data.get("stop_price"),
        submitted_at=_parse_dt(data.get("submitted_at")),
        filled_at=_parse_dt(data.get("filled_at")),
        created_at=_parse_dt(data.get("created_at")),
        updated_at=_parse_dt(data.get("updated_at")),
        provider_fields=dict(data),
    )
