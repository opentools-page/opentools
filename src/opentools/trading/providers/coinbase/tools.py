from __future__ import annotations

from opentools.core.tools import ToolSpec, tool_handler
from opentools.trading.services.core import TradingService


def coinbase_tools(service: TradingService) -> list[ToolSpec]:
    prefix = "coinbase"

    return [
        ToolSpec(
            name=f"{prefix}_get_account",
            description=(
                "Get Coinbase brokerage account info. "
                "If no account_uuid is provided, returns the primary account. "
                "If account_uuid is provided, returns that specific account. "
                "Always returns a canonical Account model."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "account_uuid": {
                        "type": "string",
                        "description": (
                            "Optional Coinbase account UUID. "
                            "If omitted, the primary account is returned."
                        ),
                    }
                },
                "additionalProperties": False,
            },
            handler=tool_handler(service.get_account),
        ),
        ToolSpec(
            name=f"{prefix}_list_accounts",
            description=(
                "List Coinbase brokerage accounts for this user. "
                "Returns the raw Coinbase JSON response "
                "including accounts, has_next, cursor, and size."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Max number of accounts per page (max 250).",
                    },
                    "cursor": {
                        "type": "string",
                        "description": "Pagination cursor from a previous response.",
                    },
                    "retail_portfolio_id": {
                        "type": "string",
                        "description": "Legacy portfolio filter (usually not needed).",
                    },
                },
                "additionalProperties": False,
            },
            handler=tool_handler(service.list_accounts),
        ),
        ToolSpec(
            name=f"{prefix}_list_assets",
            description=(
                "List Coinbase brokerage products as canonical Asset models. "
                "Under the hood this calls the /api/v3/brokerage/products endpoint "
                "and maps each product into the shared Asset schema."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": (
                            "Max number of products to return. "
                            "Note: provider may still cap page size."
                        ),
                    },
                    "asset_class": {
                        "type": "string",
                        "description": (
                            "Logical asset class filter. "
                            "Common values: 'crypto', 'spot', 'future'. "
                            "Mapped to Coinbase product_type SPOT / FUTURE."
                        ),
                    },
                    "attributes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Optional feature flags. "
                            "Use 'tradable' to request tradability status. "
                            "Use 'all' to include all products (including expired futures)."
                        ),
                    },
                },
                "additionalProperties": False,
            },
            handler=tool_handler(service.list_assets),
        ),
        ToolSpec(
            name=f"{prefix}_list_orders",
            description=(
                "List Coinbase brokerage orders with optional filters. "
                "Returns a canonical list of Order models. "
                "Only the first page of results is returned."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": (
                            "Optional Coinbase order status filter "
                            "(e.g. PENDING, OPEN, FILLED, CANCELLED)."
                        ),
                    },
                    "limit": {
                        "type": "integer",
                        "description": (
                            "Max number of orders to return (first page only)."
                        ),
                    },
                    "after": {
                        "type": "string",
                        "description": (
                            "Start date/time (RFC3339) to fetch orders from, inclusive."
                        ),
                    },
                    "until": {
                        "type": "string",
                        "description": (
                            "End date/time (RFC3339) to fetch orders until, exclusive."
                        ),
                    },
                    "symbols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Optional list of product IDs to filter by, "
                            "e.g. ['BTC-USD', 'ETH-USD']."
                        ),
                    },
                    "side": {
                        "type": "string",
                        "enum": ["buy", "sell"],
                        "description": "Order side filter. Maps to Coinbase BUY/SELL.",
                    },
                },
                "additionalProperties": False,
            },
            handler=tool_handler(service.list_orders),
        ),
        ToolSpec(
            name=f"{prefix}_get_order",
            description=(
                "Get a single Coinbase brokerage order by order_id. "
                "Returns a canonical Order model built from the full Coinbase response."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The Coinbase order_id to fetch.",
                    },
                    "nested": {
                        "type": "boolean",
                        "description": (
                            "Optional nested flag, currently unused but kept for API compatibility."
                        ),
                    },
                },
                "required": ["order_id"],
                "additionalProperties": False,
            },
            handler=tool_handler(service.get_order),
        ),
    ]
