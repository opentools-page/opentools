from __future__ import annotations

from typing import Any, Dict, List

from opentools.core.tools import ToolSpec, tool_handler
from opentools.trading.schemas import (
    Account,
    Asset,
    Clock,
    Order,
    PortfolioHistory,
    Position,
)
from opentools.trading.services.core import TradingService


def minimal(obj: Any, *, minimal: bool) -> Any:
    include_provider = not minimal
    include_provider_fields = not minimal

    if isinstance(obj, list):
        out: list[Any] = []
        for x in obj:
            if hasattr(x, "canonical_view"):
                out.append(
                    x.canonical_view(
                        include_provider=include_provider,
                        include_provider_fields=include_provider_fields,
                    )
                )
            else:
                out.append(x)
        return out

    if hasattr(obj, "canonical_view"):
        return obj.canonical_view(
            include_provider=include_provider,
            include_provider_fields=include_provider_fields,
        )

    return obj


def alpaca_tools(service: TradingService) -> list[ToolSpec]:
    prefix = "alpaca"

    # ---------- tool handlers ----------

    async def _get_account_tool() -> Dict[str, Any]:
        acct: Account = await service.get_account()
        return minimal(acct, minimal=service.minimal)

    async def _list_positions_tool() -> List[Dict[str, Any]]:
        positions: List[Position] = await service.list_positions()
        return minimal(positions, minimal=service.minimal)

    async def _get_position_tool(symbol_or_asset_id: str) -> Dict[str, Any] | None:
        pos = await service.get_position(symbol_or_asset_id)
        if pos is None:
            return None
        return minimal(pos, minimal=service.minimal)

    async def _get_clock_tool() -> Dict[str, Any]:
        clock: Clock = await service.get_clock()
        return minimal(clock, minimal=service.minimal)

    async def _list_assets_tool(
        status: str | None = None,
        asset_class: str | None = None,
        exchange: str | None = None,
        attributes: list[str] | None = None,
        limit: int | None = None,
    ) -> List[Dict[str, Any]]:
        assets: List[Asset] = await service.list_assets(
            status=status,
            asset_class=asset_class,
            exchange=exchange,
            attributes=attributes,
            limit=limit,
        )
        return minimal(assets, minimal=service.minimal)

    async def _get_asset_tool(symbol_or_asset_id: str) -> Dict[str, Any] | None:
        asset = await service.get_asset(symbol_or_asset_id)
        if asset is None:
            return None
        return minimal(asset, minimal=service.minimal)

    async def _list_orders_tool(
        status: str | None = None,
        limit: int | None = None,
        after: str | None = None,
        until: str | None = None,
        direction: str | None = None,
        nested: bool | None = None,
        symbols: list[str] | None = None,
        side: str | None = None,
        asset_class: list[str] | None = None,
        before_order_id: str | None = None,
        after_order_id: str | None = None,
    ) -> List[Dict[str, Any]]:
        orders: List[Order] = await service.list_orders(
            status=status,
            limit=limit,
            after=after,
            until=until,
            direction=direction,
            nested=nested,
            symbols=symbols,
            side=side,
            asset_class=asset_class,
            before_order_id=before_order_id,
            after_order_id=after_order_id,
        )
        return minimal(orders, minimal=service.minimal)

    async def _get_order_tool(
        order_id: str,
        nested: bool | None = None,
    ) -> Dict[str, Any] | None:
        order = await service.get_order(order_id=order_id, nested=nested)
        if order is None:
            return None
        return minimal(order, minimal=service.minimal)

    async def _get_portfolio_history_tool(
        period: str | None = None,
        timeframe: str | None = None,
        intraday_reporting: str | None = None,
        start: str | None = None,
        end: str | None = None,
        pnl_reset: str | None = None,
        cashflow_types: str | None = None,
    ) -> Dict[str, Any]:
        history: PortfolioHistory = await service.get_portfolio_history(
            period=period,
            timeframe=timeframe,
            intraday_reporting=intraday_reporting,
            start=start,
            end=end,
            pnl_reset=pnl_reset,
            cashflow_types=cashflow_types,
        )
        return minimal(history, minimal=service.minimal)

    # tool specs
    return [
        ToolSpec(
            name=f"{prefix}_get_account",
            description=(
                "Get Alpaca account info (cash, equity, buying power) "
                "as a canonical Account model. When the service is configured "
                "with minimal=True, provider metadata is omitted."
            ),
            input_schema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            handler=tool_handler(_get_account_tool),
        ),
        ToolSpec(
            name=f"{prefix}_list_positions",
            description=(
                "List Alpaca open positions as canonical Position models. "
                "When minimal=True, provider metadata is omitted."
            ),
            input_schema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            handler=tool_handler(_list_positions_tool),
        ),
        ToolSpec(
            name=f"{prefix}_get_position",
            description=(
                "Get a single Alpaca position by symbol or asset ID as a canonical "
                "Position model. When minimal=True, provider metadata is omitted."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "symbol_or_asset_id": {
                        "type": "string",
                        "description": (
                            "Ticker symbol or Alpaca asset ID to look up the position."
                        ),
                    }
                },
                "required": ["symbol_or_asset_id"],
                "additionalProperties": False,
            },
            handler=tool_handler(_get_position_tool),
        ),
        ToolSpec(
            name=f"{prefix}_get_clock",
            description=(
                "Get the Alpaca trading clock (market open/close info) "
                "as a canonical Clock model. When minimal=True, provider "
                "metadata is omitted."
            ),
            input_schema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            handler=tool_handler(_get_clock_tool),
        ),
        ToolSpec(
            name=f"{prefix}_list_assets",
            description=(
                "List Alpaca assets (stocks, etc.) as canonical Asset models "
                "with optional filters. Use `limit` to cap how many assets are "
                "returned. When minimal=True, provider metadata is omitted."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Asset status filter (e.g. 'active').",
                    },
                    "asset_class": {
                        "type": "string",
                        "description": "Asset class filter (e.g. 'us_equity').",
                    },
                    "exchange": {
                        "type": "string",
                        "description": "Exchange code (e.g. 'NYSE', 'NASDAQ').",
                    },
                    "attributes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional asset attributes.",
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 200,
                        "default": 20,
                        "description": (
                            "Maximum number of assets to return. "
                            "Defaults to 20 to avoid huge tool outputs."
                        ),
                    },
                },
                "additionalProperties": False,
            },
            handler=tool_handler(_list_assets_tool),
        ),
        ToolSpec(
            name=f"{prefix}_get_asset",
            description=(
                "Get a single Alpaca asset by symbol or asset ID as a canonical "
                "Asset model. Extra provider-specific fields live under "
                "provider_fields unless minimal=True, in which case they "
                "are omitted."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "symbol_or_asset_id": {
                        "type": "string",
                        "description": "Ticker symbol or Alpaca asset ID.",
                    }
                },
                "required": ["symbol_or_asset_id"],
                "additionalProperties": False,
            },
            handler=tool_handler(_get_asset_tool),
        ),
        ToolSpec(
            name=f"{prefix}_list_orders",
            description=(
                "List Alpaca orders with optional filters as canonical Order models. "
                "Use `limit` to cap how many orders are returned. "
                "When minimal=True, provider metadata is omitted."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Order status: 'open', 'closed', or 'all'.",
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 200,
                        "default": 20,
                        "description": (
                            "Maximum number of orders to return. "
                            "Defaults to 20 to avoid huge tool outputs."
                        ),
                    },
                    "after": {
                        "type": "string",
                        "description": "Only orders submitted after this ISO8601 timestamp.",
                    },
                    "until": {
                        "type": "string",
                        "description": "Only orders submitted until this ISO8601 timestamp.",
                    },
                    "direction": {
                        "type": "string",
                        "description": "Sort direction: 'asc' or 'desc'.",
                    },
                    "nested": {
                        "type": "boolean",
                        "description": "If true, roll up multi-leg orders under 'legs'.",
                    },
                    "symbols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by symbols, e.g. ['AAPL', 'TSLA'].",
                    },
                    "side": {
                        "type": "string",
                        "description": "Filter by side: 'buy' or 'sell'.",
                    },
                    "asset_class": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Filter by asset classes, e.g. ['us_equity', 'us_option']."
                        ),
                    },
                    "before_order_id": {
                        "type": "string",
                        "description": "Only orders submitted before this order id.",
                    },
                    "after_order_id": {
                        "type": "string",
                        "description": "Only orders submitted after this order id.",
                    },
                },
                "additionalProperties": False,
            },
            handler=tool_handler(_list_orders_tool),
        ),
        ToolSpec(
            name=f"{prefix}_get_order",
            description=(
                "Get a single Alpaca order by order ID as a canonical Order model. "
                "When minimal=True, provider metadata is omitted."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Alpaca order ID.",
                    },
                    "nested": {
                        "type": "boolean",
                        "description": "If true, include legs for multi-leg orders.",
                    },
                },
                "required": ["order_id"],
                "additionalProperties": False,
            },
            handler=tool_handler(_get_order_tool),
        ),
        ToolSpec(
            name=f"{prefix}_get_portfolio_history",
            description=(
                "Get Alpaca account portfolio history (equity and P&L timeseries) "
                "as a canonical PortfolioHistory model. When minimal=True, "
                "provider metadata is omitted."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "period": {
                        "type": "string",
                        "description": "Duration like '1D', '1W', '1M', '3M', '1A'.",
                    },
                    "timeframe": {
                        "type": "string",
                        "description": "Resolution: '1Min', '5Min', '15Min', '1H', '1D'.",
                    },
                    "intraday_reporting": {
                        "type": "string",
                        "description": (
                            "Intraday reporting mode: 'market_hours', "
                            "'extended_hours', or 'continuous'."
                        ),
                    },
                    "start": {
                        "type": "string",
                        "description": "Start timestamp (RFC3339).",
                    },
                    "end": {
                        "type": "string",
                        "description": "End timestamp (RFC3339).",
                    },
                    "pnl_reset": {
                        "type": "string",
                        "description": "PnL reset mode: 'per_day' or 'no_reset'.",
                    },
                    "cashflow_types": {
                        "type": "string",
                        "description": (
                            "Cashflow filter: 'ALL', 'NONE', or comma-separated "
                            "activity types."
                        ),
                    },
                },
                "additionalProperties": False,
            },
            handler=tool_handler(_get_portfolio_history_tool),
        ),
    ]
