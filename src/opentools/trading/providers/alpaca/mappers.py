from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ...schemas import (
    Account,
    Asset,
    Clock,
    Order,
    PortfolioHistory,
    PortfolioHistoryPoint,
    Position,
)


def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _parse_ts(value: Any) -> datetime | None:
    """
    Alpaca portfolio history timestamps can be either:
      - unix seconds (int/float)
      - RFC3339 strings
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    if isinstance(value, str):
        return _parse_dt(value)
    return None


def _extras_only(raw: dict[str, Any], *, drop_keys: set[str]) -> dict[str, Any]:
    """
    provider_fields policy:
      - keep only keys NOT already represented in canonical fields
      - also drop internal bookkeeping keys (_opentools_*)
    """
    out: dict[str, Any] = {}
    for k, v in raw.items():
        if k in drop_keys:
            continue
        if isinstance(k, str) and k.startswith("_opentools_"):
            continue
        out[k] = v
    return out


def account_from_alpaca(data: dict[str, Any]) -> Account:
    drop = {
        "id",
        "status",
        "currency",
        "cash",
        "buying_power",
        "equity",
        "portfolio_value",
        "created_at",
        "provider",  # if it ever appears
        "provider_fields",
    }

    return Account(
        provider="alpaca",
        id=data.get("id"),
        status=data.get("status"),
        currency=data.get("currency"),
        cash=data.get("cash"),
        buying_power=data.get("buying_power"),
        equity=data.get("equity"),
        portfolio_value=data.get("portfolio_value"),
        created_at=_parse_dt(data.get("created_at")),
        provider_fields=_extras_only(data, drop_keys=drop),
    )


def position_from_alpaca(data: dict[str, Any]) -> Position | None:
    symbol = data.get("symbol")
    if not symbol:
        return None

    drop = {
        "symbol",
        "qty",
        "avg_entry_price",
        "current_price",
        "market_value",
        "unrealised_pl",
        "unrealised_plpc",
        "side",
        "provider",
        "provider_fields",
    }

    return Position(
        provider="alpaca",
        symbol=symbol,
        qty=data.get("qty"),
        avg_entry_price=data.get("avg_entry_price"),
        current_price=data.get("current_price"),
        market_value=data.get("market_value"),
        unrealised_pl=data.get("unrealised_pl"),
        unrealised_plpc=data.get("unrealised_plpc"),
        side=data.get("side"),
        provider_fields=_extras_only(data, drop_keys=drop),
    )


def clock_from_alpaca(data: dict[str, Any]) -> Clock:
    drop = {
        "timestamp",
        "is_open",
        "next_open",
        "next_close",
        "provider",
        "provider_fields",
    }

    return Clock(
        provider="alpaca",
        timestamp=_parse_dt(data.get("timestamp")),
        is_open=data.get("is_open"),
        next_open=_parse_dt(data.get("next_open")),
        next_close=_parse_dt(data.get("next_close")),
        provider_fields=_extras_only(data, drop_keys=drop),
    )


def asset_from_alpaca(data: dict[str, Any]) -> Asset | None:
    symbol = data.get("symbol")
    if not symbol:
        return None

    drop = {
        "id",
        "symbol",
        "name",
        "exchange",
        "asset_class",
        "status",
        "tradable",
        "marginable",
        "shortable",
        "easy_to_borrow",
        "fractionable",
        "provider",
        "provider_fields",
    }

    return Asset(
        provider="alpaca",
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
        provider_fields=_extras_only(data, drop_keys=drop),
    )


def order_from_alpaca(data: dict[str, Any]) -> Order | None:
    order_id = data.get("id")
    if not order_id:
        return None

    drop = {
        "id",
        "client_order_id",
        "symbol",
        "side",
        "type",
        "time_in_force",
        "status",
        "qty",
        "notional",
        "filled_qty",
        "filled_avg_price",
        "limit_price",
        "stop_price",
        "submitted_at",
        "filled_at",
        "created_at",
        "updated_at",
        "provider",
        "provider_fields",
    }

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
        provider_fields=_extras_only(data, drop_keys=drop),
    )


def portfolio_history_from_alpaca(data: dict[str, Any]) -> PortfolioHistory:
    timestamps = data.get("timestamp") or []
    equities = data.get("equity") or []
    pls = data.get("profit_loss") or []
    pl_pcts = data.get("profit_loss_pct") or []

    n = min(len(timestamps), len(equities))
    points: list[PortfolioHistoryPoint] = []

    for i in range(n):
        ts = _parse_ts(timestamps[i])
        if ts is None:
            continue

        equity_raw = equities[i]
        if equity_raw is None:
            continue

        pl_val = None
        if i < len(pls) and pls[i] is not None:
            pl_val = float(pls[i])

        pl_pct_val = None
        if i < len(pl_pcts) and pl_pcts[i] is not None:
            pl_pct_val = float(pl_pcts[i])

        points.append(
            PortfolioHistoryPoint(
                timestamp=ts,
                equity=float(equity_raw),
                profit_loss=pl_val,
                profit_loss_pct=pl_pct_val,
            )
        )

    drop = {
        "timeframe",
        "base_value",
        "base_value_asof",
        "timestamp",
        "equity",
        "profit_loss",
        "profit_loss_pct",
        "provider",
        "provider_fields",
    }

    return PortfolioHistory(
        provider="alpaca",
        timeframe=data.get("timeframe"),
        base_value=float(data["base_value"])
        if data.get("base_value") is not None
        else None,
        base_value_asof=_parse_ts(data.get("base_value_asof")),
        points=points,
        provider_fields=_extras_only(data, drop_keys=drop),
    )
