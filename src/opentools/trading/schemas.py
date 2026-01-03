from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TradingModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="after")
    def _normalise_datetimes_to_utc(self) -> "TradingModel":
        fields = getattr(self.__class__, "model_fields", {}) or {}

        for name in fields:
            v = getattr(self, name, None)
            if isinstance(v, datetime):
                if v.tzinfo is None:
                    v = v.replace(tzinfo=timezone.utc)
                else:
                    v = v.astimezone(timezone.utc)
                setattr(self, name, v)

        return self

    def canonical_view(
        self,
        *,
        include_provider: bool = True,
        include_provider_fields: bool = True,
    ) -> dict[str, Any]:
        INTERNAL_PREFIXES: tuple[str, ...] = ("_opentools_",)

        seen_ids: set[int] = set()

        def walk(value: Any) -> Any:
            if isinstance(value, TradingModel):
                vid = id(value)
                if vid in seen_ids:
                    return "<recursion>"
                seen_ids.add(vid)

                out_obj: dict[str, Any] = {}
                for field_name in type(value).model_fields:
                    if not include_provider and field_name == "provider":
                        continue
                    if not include_provider_fields and field_name == "provider_fields":
                        continue
                    out_obj[field_name] = walk(getattr(value, field_name))

                seen_ids.remove(vid)
                return out_obj

            if isinstance(value, BaseModel):
                return value.model_dump()

            if isinstance(value, dict):
                out_map: dict[str, Any] = {}
                for k, v in value.items():
                    if isinstance(k, str) and k.startswith(INTERNAL_PREFIXES):
                        continue
                    if (not include_provider and k == "provider") or (
                        not include_provider_fields and k == "provider_fields"
                    ):
                        continue
                    out_map[k] = walk(v)
                return out_map

            if isinstance(value, (list, tuple)):
                return [walk(v) for v in value]

            return value

        return walk(self)


# account
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


# position
class Position(TradingModel):
    provider: str | None = None
    symbol: str
    qty: str | None = None
    avg_entry_price: str | None = None
    current_price: str | None = None
    market_value: str | None = None

    # American spelling is canonical
    unrealized_pl: str | None = None
    unrealized_plpc: str | None = None

    side: Literal["long", "short"] | None = None
    provider_fields: dict[str, Any] = Field(default_factory=dict)


# clock (trading times - fiat only)
class Clock(TradingModel):
    provider: str | None = None
    timestamp: datetime | None = None
    is_open: bool | None = None
    next_open: datetime | None = None
    next_close: datetime | None = None
    provider_fields: Dict[str, Any] = Field(default_factory=dict)


# assets
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


# order
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


# portfolio
class PortfolioHistory(TradingModel):
    provider: str | None = None
    timeframe: str | None = None

    base_value: float | None = None
    base_value_asof: datetime | None = None

    points: List["PortfolioHistoryPoint"] = Field(default_factory=list)
    provider_fields: Dict[str, Any] = Field(default_factory=dict)


class PortfolioHistoryPoint(TradingModel):
    timestamp: datetime
    equity: float
    profit_loss: float | None = None
    profit_loss_pct: float | None = None


class Portfolio(TradingModel):
    provider: str | None = None
    id: str | None = None
    name: str | None = None
    type: str | None = None
    deleted: bool | None = None
    provider_fields: dict[str, Any] = Field(default_factory=dict)


class MoneyAmount(TradingModel):
    value: str | None = None
    currency: str | None = None


class PortfolioBalances(TradingModel):
    total_balance: MoneyAmount | None = None
    total_futures_balance: MoneyAmount | None = None
    total_cash_equivalent_balance: MoneyAmount | None = None
    total_crypto_balance: MoneyAmount | None = None

    futures_unrealized_pnl: MoneyAmount | None = None
    perp_unrealized_pnl: MoneyAmount | None = None

    provider_fields: dict[str, Any] = Field(default_factory=dict)


class PortfolioBreakdown(TradingModel):
    provider: str | None = None
    portfolio: Portfolio | None = None
    balances: PortfolioBalances | None = None

    spot_positions: list[Position] = Field(default_factory=list)
    perp_positions: list[Position] = Field(default_factory=list)
    futures_positions: list[Position] = Field(default_factory=list)

    provider_fields: dict[str, Any] = Field(default_factory=dict)
