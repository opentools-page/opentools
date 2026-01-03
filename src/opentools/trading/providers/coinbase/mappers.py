from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, cast

from ...schemas import (
    Account,
    Asset,
    Clock,
    MoneyAmount,
    Order,
    Portfolio,
    PortfolioBalances,
    PortfolioBreakdown,
    Position,
)

_OPENTOOLS_INTERNAL_PREFIXES: tuple[str, ...] = ("_opentools_",)


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


def _extras(raw: dict[str, Any], used_keys: set[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in raw.items():
        if k in used_keys:
            continue
        if isinstance(k, str) and k.startswith(_OPENTOOLS_INTERNAL_PREFIXES):
            continue
        out[k] = v
    return out


def _money(x: Any) -> MoneyAmount | None:
    if not isinstance(x, dict):
        return None
    return MoneyAmount(
        value=_to_str(x.get("value")),
        currency=_to_str(x.get("currency")),
    )


def _nested_money_value(x: Any) -> str | None:
    if not isinstance(x, dict):
        return None
    native = x.get("userNativeCurrency")
    raw = x.get("rawCurrency")
    if isinstance(native, dict) and native.get("value") is not None:
        return _to_str(native.get("value"))
    if isinstance(raw, dict) and raw.get("value") is not None:
        return _to_str(raw.get("value"))
    return None


# accounts
def account_from_coinbase(data: dict[str, Any]) -> Account:
    available_balance = data.get("available_balance") or {}
    cash_value = available_balance.get("value")
    cash_str = _to_str(cash_value) if cash_value is not None else None

    used = {"uuid", "active", "currency", "available_balance", "created_at"}
    provider_fields = _extras(data, used)

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

    product_id = data.get("product_id")
    side = _normalize_side(data.get("side"))
    status = data.get("status")

    created_dt = _parse_dt(data.get("created_time") or data.get("created_at"))
    last_fill_dt = _parse_dt(data.get("last_fill_time"))

    order_type = data.get("order_type")
    time_in_force = data.get("time_in_force")

    filled_size = _to_str(data.get("filled_size"))
    avg_filled_price = _to_str(data.get("average_filled_price"))

    used = {
        "order_id",
        "client_order_id",
        "product_id",
        "side",
        "status",
        "created_time",
        "created_at",
        "last_fill_time",
        "order_type",
        "time_in_force",
        "filled_size",
        "average_filled_price",
    }
    provider_fields = _extras(data, used)

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

    base_name = data.get("base_name")
    quote_name = data.get("quote_name")
    display_name = (
        data.get("display_name_overwrite") or data.get("display_name") or None
    )
    if not display_name and (base_name or quote_name):
        parts = [p for p in (base_name, quote_name) if p]
        display_name = " / ".join(parts) if parts else None

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

    used = {
        "product_id",
        "base_name",
        "quote_name",
        "display_name_overwrite",
        "display_name",
        "product_type",
        "product_venue",
        "status",
        "trading_disabled",
        "view_only",
    }
    provider_fields = _extras(data, used)

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

    used = {"uuid", "name", "type", "deleted"}
    provider_fields = _extras(data, used)

    return Portfolio(
        provider="coinbase",
        id=uuid,
        name=data.get("name"),
        type=data.get("type"),
        deleted=data.get("deleted"),
        provider_fields=provider_fields,
    )


def portfolio_breakdown_from_coinbase(bd: dict[str, Any]) -> PortfolioBreakdown:
    portfolio = portfolio_from_coinbase(bd.get("portfolio") or {})

    balances_raw = bd.get("portfolio_balances") or {}
    balances: PortfolioBalances | None = None
    if isinstance(balances_raw, dict) and balances_raw:
        used_bal = {
            "total_balance",
            "total_futures_balance",
            "total_cash_equivalent_balance",
            "total_crypto_balance",
            "futures_unrealized_pnl",
            "perp_unrealized_pnl",
        }

        balances = PortfolioBalances(
            total_balance=_money(balances_raw.get("total_balance")),
            total_futures_balance=_money(balances_raw.get("total_futures_balance")),
            total_cash_equivalent_balance=_money(
                balances_raw.get("total_cash_equivalent_balance")
            ),
            total_crypto_balance=_money(balances_raw.get("total_crypto_balance")),
            futures_unrealized_pnl=_money(balances_raw.get("futures_unrealized_pnl")),
            perp_unrealized_pnl=_money(balances_raw.get("perp_unrealized_pnl")),
            provider_fields=_extras(balances_raw, used_bal),
        )

    spot_raw = bd.get("spot_positions") or []
    perp_raw = bd.get("perp_positions") or []
    futs_raw = bd.get("futures_positions") or []

    used_bd = {
        "portfolio",
        "portfolio_balances",
        "spot_positions",
        "perp_positions",
        "futures_positions",
    }
    provider_fields = _extras(bd, used_bd)

    return PortfolioBreakdown(
        provider="coinbase",
        portfolio=portfolio,
        balances=balances,
        spot_positions=[
            p for p in (spot_position_from_coinbase(x) for x in spot_raw) if p
        ],
        perp_positions=[
            p for p in (perp_position_from_coinbase(x) for x in perp_raw) if p
        ],
        futures_positions=[
            p for p in (futures_position_from_coinbase(x) for x in futs_raw) if p
        ],
        provider_fields=provider_fields,
    )


# positions
def position_from_coinbase(data: dict[str, Any]) -> Position | None:
    kind = data.get("_opentools_position_kind")

    if kind == "spot":
        return spot_position_from_coinbase(data)
    if kind == "perp":
        return perp_position_from_coinbase(data)
    if kind in ("future", "futures"):
        return futures_position_from_coinbase(data)

    if "asset" in data and "total_balance_crypto" in data:
        return spot_position_from_coinbase(data)
    if "position_side" in data and "net_size" in data:
        return perp_position_from_coinbase(data)
    if "contract_size" in data or "expiry" in data:
        return futures_position_from_coinbase(data)

    return None


def spot_position_from_coinbase(data: dict[str, Any]) -> Position | None:
    asset = data.get("asset") or data.get("symbol")
    if not asset:
        return None

    avg_entry = data.get("average_entry_price") or {}
    avg_entry_val = avg_entry.get("value")

    qty = data.get("total_balance_crypto")
    unrealized_pl = data.get("unrealized_pnl")

    used = {
        "asset",
        "symbol",
        "average_entry_price",
        "total_balance_crypto",
        "total_balance_fiat",
        "unrealized_pnl",
    }
    provider_fields = _extras(data, used)

    return Position(
        provider="coinbase",
        symbol=str(asset),
        qty=_to_str(qty),
        avg_entry_price=_to_str(avg_entry_val),
        current_price=None,
        market_value=_to_str(data.get("total_balance_fiat")),
        unrealized_pl=_to_str(unrealized_pl),
        unrealized_plpc=None,
        side="long",
        provider_fields=provider_fields,
    )


def perp_position_from_coinbase(data: dict[str, Any]) -> Position | None:
    symbol = data.get("symbol") or data.get("product_id") or data.get("product_uuid")
    if not symbol:
        return None

    side_raw = (data.get("position_side") or "").upper()
    side: Literal["long", "short"] | None = None
    if "LONG" in side_raw:
        side = "long"
    elif "SHORT" in side_raw:
        side = "short"

    qty = data.get("net_size")
    mark_price = _nested_money_value(data.get("mark_price"))
    unrealized_pl = _nested_money_value(data.get("unrealized_pnl"))
    avg_entry_price = _nested_money_value(data.get("vwap"))
    notional = _nested_money_value(data.get("position_notional"))

    used = {
        "symbol",
        "product_id",
        "product_uuid",
        "position_side",
        "net_size",
        "mark_price",
        "unrealized_pnl",
        "vwap",
        "position_notional",
    }
    provider_fields = _extras(data, used)

    return Position(
        provider="coinbase",
        symbol=_to_str(symbol) or str(symbol),
        qty=_to_str(qty),
        avg_entry_price=_to_str(avg_entry_price),
        current_price=_to_str(mark_price),
        market_value=_to_str(notional),
        unrealized_pl=_to_str(unrealized_pl),
        unrealized_plpc=None,
        side=side,
        provider_fields=provider_fields,
    )


def futures_position_from_coinbase(data: dict[str, Any]) -> Position | None:
    symbol = (
        data.get("product_id")
        or data.get("underlying_asset")
        or data.get("product_name")
    )
    if not symbol:
        return None

    side_raw = (data.get("side") or "").upper()
    side: Literal["long", "short"] | None = None
    if "LONG" in side_raw:
        side = "long"
    elif "SHORT" in side_raw:
        side = "short"

    used = {
        "product_id",
        "underlying_asset",
        "product_name",
        "side",
        "amount",
        "avg_entry_price",
        "current_price",
        "notional_value",
        "unrealized_pnl",
    }
    provider_fields = _extras(data, used)

    return Position(
        provider="coinbase",
        symbol=_to_str(symbol) or str(symbol),
        qty=_to_str(data.get("amount")),
        avg_entry_price=_to_str(data.get("avg_entry_price")),
        current_price=_to_str(data.get("current_price")),
        market_value=_to_str(data.get("notional_value")),
        unrealized_pl=_to_str(data.get("unrealized_pnl")),
        unrealized_plpc=None,
        side=side,
        provider_fields=provider_fields,
    )


# stub
def clock_from_coinbase(data: dict[str, Any]) -> Clock:
    provider_fields = _extras(data, used_keys=set())
    return Clock(
        provider="coinbase",
        timestamp=None,
        is_open=None,
        next_open=None,
        next_close=None,
        provider_fields=provider_fields,
    )
