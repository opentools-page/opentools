from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class FinanceModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Account(FinanceModel):
    id: str | None = None
    status: str | None = None
    currency: str | None = None
    cash: str | None = None
    buying_power: str | None = None
    equity: str | None = None
    portfolio_value: str | None = None
    created_at: str | None = None
    provider_fields: dict[str, Any] = Field(default_factory=dict)


class Position(FinanceModel):
    symbol: str
    qty: str | None = None
    avg_entry_price: str | None = None
    current_price: str | None = None
    market_value: str | None = None
    unrealized_pl: str | None = None
    unrealized_plpc: str | None = None
    side: Literal["long", "short"] | None = None
    provider_fields: dict[str, Any] = Field(default_factory=dict)


class Order(FinanceModel):
    id: str | None = None
    client_order_id: str | None = None
    created_at: str | None = None
    submitted_at: str | None = None
    filled_at: str | None = None
    symbol: str | None = None
    side: Literal["buy", "sell"] | None = None
    type: str | None = None  # market/limit/stop
    time_in_force: str | None = None
    qty: str | None = None
    notional: str | None = None
    filled_qty: str | None = None
    filled_avg_price: str | None = None
    status: str | None = None
    provider_fields: dict[str, Any] = Field(default_factory=dict)


class Quote(FinanceModel):
    symbol: str
    price: str | None = None
    bid: str | None = None
    ask: str | None = None
    asof: str | None = None

    provider_fields: dict[str, Any] = Field(default_factory=dict)
