from __future__ import annotations

from opentools.core.tools import ToolSpec, tool_handler


def alpaca_tools(service) -> list[ToolSpec]:
    return [
        ToolSpec(
            name="get_account",
            description="Get Alpaca account info (cash, equity, buying power).",
            input_schema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            handler=tool_handler(service.get_account),
        ),
        ToolSpec(
            name="list_positions",
            description="List Alpaca open positions.",
            input_schema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            handler=tool_handler(service.list_positions),
        ),
        ToolSpec(
            name="get_clock",
            description="Get the Alpaca trading clock (market open/close info).",
            input_schema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            handler=tool_handler(service.get_clock),
        ),
        ToolSpec(
            name="list_assets",
            description=(
                "List Alpaca assets (stocks, etc.) with optional filters. "
                "Use `limit` to cap how many assets are returned."
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
            handler=tool_handler(service.list_assets),
        ),
        ToolSpec(
            name="get_asset",
            description="Get a single Alpaca asset by symbol or asset ID.",
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
            handler=tool_handler(service.get_asset),
        ),
        ToolSpec(
            name="list_orders",
            description=(
                "List Alpaca orders with optional filters. "
                "Use `limit` to cap how many orders are returned."
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
            handler=tool_handler(service.list_orders),
        ),
        ToolSpec(
            name="get_order",
            description="Get a single Alpaca order by order ID.",
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
            handler=tool_handler(service.get_order),
        ),
        ToolSpec(
            name="get_portfolio_history",
            description=(
                "Get Alpaca account portfolio history (equity and P&L timeseries). "
                "Use period/timeframe for range, and intraday_reporting/pnl_reset "
                "for intraday behaviour."
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
            handler=tool_handler(service.get_portfolio_history),
        ),
    ]
