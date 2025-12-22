from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Literal

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
