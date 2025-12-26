# opentools/trading/providers/coinbase/mappers.py
from __future__ import annotations

from datetime import datetime
from typing import Any

from ...schemas import (
    Account,
    Asset,
    Clock,
    Order,
    PortfolioHistory,
    Position,
)


def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def account_from_coinbase(data: dict[str, Any]) -> Account:
    available_balance = data.get("available_balance") or {}
    cash_value = available_balance.get("value")

    return Account(
        provider="coinbase",
        id=data.get("uuid"),
        status="active" if data.get("active") else "inactive",
        currency=data.get("currency"),
        cash=cash_value,
        buying_power=cash_value,  # best-effort;
        equity=cash_value,
        portfolio_value=cash_value,
        created_at=_parse_dt(data.get("created_at")),
        provider_fields=dict(data),
    )


# placeholders


def position_from_coinbase(data: dict[str, Any]) -> Position | None:
    # No real positions mapping yet
    return None


def clock_from_coinbase(data: dict[str, Any]) -> Clock:
    # Coinbase doesn't expose a simple "clock" like Alpaca.
    # For now just stash raw payload.
    return Clock(
        provider="coinbase",
        timestamp=None,
        is_open=None,
        next_open=None,
        next_close=None,
        provider_fields=dict(data),
    )


def asset_from_coinbase(data: dict[str, Any]) -> Asset | None:
    return None


def order_from_coinbase(data: dict[str, Any]) -> Order | None:
    return None


def portfolio_history_from_coinbase(data: dict[str, Any]) -> PortfolioHistory:
    # Minimal stub; no points yet.
    return PortfolioHistory(
        provider="coinbase",
        timeframe=None,
        base_value=None,
        base_value_asof=None,
        points=[],
        provider_fields=dict(data),
    )
