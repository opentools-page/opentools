from __future__ import annotations

from opentools.core.tools import ToolSpec, tool_handler
from opentools.trading.services.core import TradingService


def coinbase_tools(service: TradingService) -> list[ToolSpec]:
    prefix = "coinbase"

    return [
        ToolSpec(
            name=f"{prefix}_get_account",
            description=(
                "Get Coinbase brokerage account info as a canonical Account model. "
                "If no account_uuid is provided, returns the primary account. "
                "If account_uuid is provided, returns that specific account. "
                "Raw provider data is still available under provider_fields."
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
                "List Coinbase brokerage accounts for this user as canonical "
                "Account models. Under the hood this calls the Coinbase "
                "accounts API and maps each account into the shared Account "
                "schema; original fields live under provider_fields."
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
            name=f"{prefix}_list_portfolios",
            description=(
                "List Coinbase portfolios for this user. "
                "Returns the raw list of portfolio objects from Coinbase "
                "(not yet mapped into a canonical Portfolio model)."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "portfolio_type": {
                        "type": "string",
                        "description": (
                            "Optional portfolio type filter, e.g. 'DEFAULT', "
                            "'CONSUMER', 'INTX', or 'UNDEFINED' to match Coinbase docs."
                        ),
                    },
                },
                "additionalProperties": False,
            },
            handler=tool_handler(service.list_portfolios),
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
            name=f"{prefix}_get_asset",
            description=(
                "Get a single Coinbase brokerage product by product_id "
                "(e.g. 'BTC-USD') as a canonical Asset model. "
                "Extra provider-specific fields live under provider_fields."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "symbol_or_asset_id": {
                        "type": "string",
                        "description": (
                            "Coinbase product_id / trading pair "
                            "(e.g. 'BTC-USD', 'ETH-USD')."
                        ),
                    },
                },
                "required": ["symbol_or_asset_id"],
                "additionalProperties": False,
            },
            handler=tool_handler(service.get_asset),
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
                "Get a single Coinbase brokerage order by order_id as a canonical "
                "Order model built from the full Coinbase response."
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
                            "Optional nested flag, currently unused but kept "
                            "for API compatibility."
                        ),
                    },
                },
                "required": ["order_id"],
                "additionalProperties": False,
            },
            handler=tool_handler(service.get_order),
        ),
    ]
