from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, cast

from ...schemas import Account, Asset, Clock, Order, Portfolio, Position


def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _to_str(v: Any) -> str | None:
    if v is None:
        return None
    return str(v)


def _normalize_side(side: str | None) -> Literal["buy", "sell"] | None:
    if not side:
        return None

    s = side.lower()
    if s in ("buy", "sell"):
        return cast(Literal["buy", "sell"], s)

    return None


def account_from_coinbase(data: dict[str, Any]) -> Account:
    available_balance = data.get("available_balance") or {}
    cash_value = available_balance.get("value")

    provider_fields = dict(data)

    if data.get("_opentools_primary_fallback"):
        provider_fields["_opentools_primary_fallback"] = True

    cash_str = _to_str(cash_value) if cash_value is not None else None

    return Account(
        provider="coinbase",
        id=data.get("uuid"),
        status="active" if data.get("active") else "inactive",
        currency=data.get("currency"),
        cash=cash_str,
        buying_power=cash_str,
        equity=cash_str,
        portfolio_value=cash_str,
        created_at=_parse_dt(data.get("created_at")),
        provider_fields=provider_fields,
    )


# orders
def order_from_coinbase(data: dict[str, Any]) -> Order | None:
    order_id = data.get("order_id")
    if not order_id:
        return None

    provider_fields = dict(data)

    product_id = data.get("product_id")
    side = _normalize_side(data.get("side"))
    status = data.get("status")

    created_dt = _parse_dt(data.get("created_time") or data.get("created_at"))
    last_fill_dt = _parse_dt(data.get("last_fill_time"))

    order_type = data.get("order_type")
    time_in_force = data.get("time_in_force")

    filled_size = _to_str(data.get("filled_size"))
    avg_filled_price = _to_str(data.get("average_filled_price"))

    return Order(
        provider="coinbase",
        id=order_id,
        client_order_id=_to_str(data.get("client_order_id")),
        symbol=product_id,
        side=side,
        type=order_type,
        time_in_force=time_in_force,
        status=status,
        qty=None,
        notional=None,
        filled_qty=filled_size,
        filled_avg_price=avg_filled_price,
        limit_price=None,
        stop_price=None,
        submitted_at=created_dt,
        filled_at=last_fill_dt,
        created_at=created_dt,
        updated_at=last_fill_dt,
        provider_fields=provider_fields,
    )


# assets
def asset_from_coinbase(data: dict[str, Any]) -> Asset | None:
    product_id = data.get("product_id")
    if not product_id:
        return None

    provider_fields = dict(data)

    base_name = data.get("base_name")
    quote_name = data.get("quote_name")
    display_name = (
        data.get("display_name_overwrite") or data.get("display_name") or None
    )
    if not display_name and (base_name or quote_name):
        parts = [p for p in [base_name, quote_name] if p]
        if parts:
            display_name = " / ".join(parts)

    product_type = data.get("product_type")
    if product_type == "SPOT":
        asset_class = "crypto"
    elif product_type == "FUTURE":
        asset_class = "future"
    else:
        asset_class = product_type

    trading_disabled = data.get("trading_disabled")
    view_only = data.get("view_only")

    if trading_disabled is None and view_only is None:
        tradable: bool | None = None
    else:
        tradable = bool(not trading_disabled and not view_only)

    return Asset(
        provider="coinbase",
        id=product_id,
        symbol=product_id,
        name=display_name,
        exchange=_to_str(data.get("product_venue")) or "coinbase",
        asset_class=_to_str(asset_class),
        status=_to_str(data.get("status")),
        tradable=tradable,
        marginable=None,
        shortable=None,
        easy_to_borrow=None,
        fractionable=None,
        provider_fields=provider_fields,
    )


# portfolios
def portfolio_from_coinbase(data: dict[str, Any]) -> Portfolio | None:
    uuid = data.get("uuid")
    if not uuid:
        return None

    return Portfolio(
        provider="coinbase",
        id=uuid,
        name=data.get("name"),
        type=data.get("type"),
        deleted=data.get("deleted"),
        provider_fields=dict(data),
    )


# stubs
def position_from_coinbase(data: dict[str, Any]) -> Position | None:
    return None


def clock_from_coinbase(data: dict[str, Any]) -> Clock:
    return Clock(
        provider="coinbase",
        timestamp=None,
        is_open=None,
        next_open=None,
        next_close=None,
        provider_fields=dict(data),
    )
