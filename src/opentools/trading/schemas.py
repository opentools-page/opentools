from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, ConfigDict, Field


class TradingModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Account(TradingModel):
    provider: str | None = None
    id: str | None = None
    status: str | None = None
    currency: str | None = None
    cash: str | None = None
    buying_power: str | None = None
    equity: str | None = None
    portfolio_value: str | None = None
    created_at: datetime | None = None
    provider_fields: dict[str, Any] = Field(default_factory=dict)


class Position(TradingModel):
    provider: str | None = None
    symbol: str
    qty: str | None = None
    avg_entry_price: str | None = None
    current_price: str | None = None
    market_value: str | None = None
    unrealized_pl: str | None = None
    unrealized_plpc: str | None = None
    side: Literal["long", "short"] | None = None
    provider_fields: dict[str, Any] = Field(default_factory=dict)


class Clock(TradingModel):
    provider: str | None = None
    timestamp: datetime | None = None
    is_open: bool | None = None
    next_open: datetime | None = None
    next_close: datetime | None = None
    provider_fields: Dict[str, Any] = Field(default_factory=dict)


class Asset(TradingModel):
    provider: str | None = None
    id: str | None = None
    symbol: str
    name: str | None = None
    exchange: str | None = None
    asset_class: str | None = None
    status: str | None = None
    tradable: bool | None = None
    marginable: bool | None = None
    shortable: bool | None = None
    easy_to_borrow: bool | None = None
    fractionable: bool | None = None
    provider_fields: dict[str, Any] = Field(default_factory=dict)


class Order(TradingModel):
    provider: str | None = None

    id: str | None = None
    client_order_id: str | None = None
    symbol: str | None = None
    side: Literal["buy", "sell"] | None = None
    type: str | None = None
    time_in_force: str | None = None
    status: str | None = None

    qty: str | None = None
    notional: str | None = None
    filled_qty: str | None = None
    filled_avg_price: str | None = None

    limit_price: str | None = None
    stop_price: str | None = None

    submitted_at: datetime | None = None
    filled_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    provider_fields: dict[str, Any] = Field(default_factory=dict)


class PortfolioHistoryPoint(TradingModel):
    timestamp: datetime
    equity: float
    profit_loss: float | None = None
    profit_loss_pct: float | None = None


class PortfolioHistory(TradingModel):
    provider: str | None = None
    timeframe: str | None = None

    base_value: float | None = None
    base_value_asof: datetime | None = None

    points: List[PortfolioHistoryPoint] = Field(default_factory=list)
    provider_fields: Dict[str, Any] = Field(default_factory=dict)
