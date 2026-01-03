from __future__ import annotations

from typing import Any, Dict, List

from opentools.core.tools import ToolSpec, tool_handler
from opentools.trading.schemas import (
    Account,
    Asset,
    Order,
    Portfolio,
    PortfolioBreakdown,
    Position,
)
from opentools.trading.services.core import TradingService

from ...utils import minimal


def coinbase_tools(service: TradingService) -> list[ToolSpec]:
    prefix = "coinbase"

    # accounts
    async def _get_account_tool(account_uuid: str | None = None) -> Dict[str, Any]:
        acct: Account = await service.get_account(account_uuid)
        return minimal(acct, minimal=service.minimal)

    async def _list_accounts_tool(
        limit: int | None = None,
        cursor: str | None = None,
        retail_portfolio_id: str | None = None,
    ) -> List[Dict[str, Any]]:
        accounts: List[Account] = await service.list_accounts(
            limit=limit,
            cursor=cursor,
            retail_portfolio_id=retail_portfolio_id,
        )
        return minimal(accounts, minimal=service.minimal)

    # portfolios
    async def _list_portfolios_tool(
        portfolio_type: str | None = None,
    ) -> List[Dict[str, Any]]:
        portfolios: List[Portfolio] = await service.list_portfolios(
            portfolio_type=portfolio_type
        )
        return minimal(portfolios, minimal=service.minimal)

    async def _get_portfolio_breakdown_tool(
        portfolio_uuid: str,
        currency: str | None = None,
    ) -> Dict[str, Any]:
        """
        Coinbase portfolio breakdown = snapshot of balances + positions.
        Returns canonical PortfolioBreakdown (then minimal()'d if configured).
        """
        bd: PortfolioBreakdown = await service.get_portfolio_breakdown(
            portfolio_uuid=portfolio_uuid,
            currency=currency,
        )
        return minimal(bd, minimal=service.minimal)

    # positions
    async def _list_positions_tool(
        portfolio_type: str | None = None,
        currency: str | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Returns canonical Position models.
        For Coinbase, this is derived from portfolio breakdown and flattened
        spot/perp/futures positions.
        """
        positions: List[Position] = await service.list_positions(
            portfolio_type=portfolio_type,
            currency=currency,
        )
        return minimal(positions, minimal=service.minimal)

    # assets
    async def _list_assets_tool(
        limit: int | None = None,
        asset_class: str | None = None,
        attributes: list[str] | None = None,
    ) -> List[Dict[str, Any]]:
        assets: List[Asset] = await service.list_assets(
            limit=limit,
            asset_class=asset_class,
            attributes=attributes,
        )
        return minimal(assets, minimal=service.minimal)

    async def _get_asset_tool(symbol_or_asset_id: str) -> Dict[str, Any] | None:
        asset = await service.get_asset(symbol_or_asset_id)
        if asset is None:
            return None
        return minimal(asset, minimal=service.minimal)

    # orders
    async def _list_orders_tool(
        status: str | None = None,
        limit: int | None = None,
        after: str | None = None,
        until: str | None = None,
        symbols: list[str] | None = None,
        side: str | None = None,
    ) -> List[Dict[str, Any]]:
        orders: List[Order] = await service.list_orders(
            status=status,
            limit=limit,
            after=after,
            until=until,
            symbols=symbols,
            side=side,
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

    # tool specs
    return [
        ToolSpec(
            name=f"{prefix}_get_account",
            description=(
                "Get Coinbase brokerage account info as a canonical Account model. "
                "If no account_uuid is provided, returns the primary account. "
                "When the service is configured with minimal=True, provider metadata is omitted."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "account_uuid": {
                        "type": "string",
                        "description": (
                            "Optional Coinbase account UUID. If omitted, the primary account is returned."
                        ),
                    }
                },
                "additionalProperties": False,
            },
            handler=tool_handler(_get_account_tool),
        ),
        ToolSpec(
            name=f"{prefix}_list_accounts",
            description=(
                "List Coinbase brokerage accounts for this user as canonical Account models. "
                "When the service is configured with minimal=True, provider metadata is omitted."
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
            handler=tool_handler(_list_accounts_tool),
        ),
        ToolSpec(
            name=f"{prefix}_list_portfolios",
            description=(
                "List Coinbase portfolios for this user as canonical Portfolio models "
                "(id, name, type, deleted). When minimal=True, provider metadata is omitted."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "portfolio_type": {
                        "type": "string",
                        "description": (
                            "Optional portfolio type filter, e.g. 'DEFAULT', "
                            "'CONSUMER', 'INTX', or 'UNDEFINED' (Coinbase terminology)."
                        ),
                    },
                },
                "additionalProperties": False,
            },
            handler=tool_handler(_list_portfolios_tool),
        ),
        ToolSpec(
            name=f"{prefix}_get_portfolio_breakdown",
            description=(
                "Get Coinbase portfolio breakdown (balances + positions) for a given portfolio UUID. "
                "Returns a canonical PortfolioBreakdown model. When minimal=True, provider metadata is omitted."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "portfolio_uuid": {
                        "type": "string",
                        "description": "The Coinbase portfolio UUID.",
                    },
                    "currency": {
                        "type": "string",
                        "description": "Optional currency code (e.g. 'USD').",
                    },
                },
                "required": ["portfolio_uuid"],
                "additionalProperties": False,
            },
            handler=tool_handler(_get_portfolio_breakdown_tool),
        ),
        ToolSpec(
            name=f"{prefix}_list_positions",
            description=(
                "List Coinbase positions as canonical Position models. "
                "Coinbase positions are derived from portfolio breakdown and flattened across "
                "spot_positions, perp_positions, and futures_positions. "
                "When minimal=True, provider metadata is omitted."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "portfolio_type": {
                        "type": "string",
                        "description": (
                            "Optional portfolio type filter to choose which portfolio UUID is used "
                            "(e.g. 'DEFAULT', 'UNDEFINED'). If omitted, DEFAULT is tried first."
                        ),
                    },
                    "currency": {
                        "type": "string",
                        "description": "Optional currency code (e.g. 'USD') for breakdown valuation fields.",
                    },
                },
                "additionalProperties": False,
            },
            handler=tool_handler(_list_positions_tool),
        ),
        ToolSpec(
            name=f"{prefix}_list_assets",
            description=(
                "List Coinbase brokerage products as canonical Asset models. "
                "Under the hood this calls the /api/v3/brokerage/products endpoint and maps each "
                "product into the shared Asset schema. When minimal=True, provider metadata is omitted."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": (
                            "Max number of products to return. Note: provider may still cap page size."
                        ),
                    },
                    "asset_class": {
                        "type": "string",
                        "description": (
                            "Logical asset class filter. Common values: 'crypto', 'spot', 'future'. "
                            "Mapped to Coinbase product_type SPOT / FUTURE where applicable."
                        ),
                    },
                    "attributes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": (
                            "Optional feature flags. Use 'tradable' to request tradability status. "
                            "Use 'all' to include all products (including expired futures)."
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
                "Get a single Coinbase brokerage product by product_id (e.g. 'BTC-USD') "
                "as a canonical Asset model. Extra provider-specific fields live under provider_fields "
                "unless minimal=True."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "symbol_or_asset_id": {
                        "type": "string",
                        "description": "Coinbase product_id / trading pair (e.g. 'BTC-USD').",
                    },
                },
                "required": ["symbol_or_asset_id"],
                "additionalProperties": False,
            },
            handler=tool_handler(_get_asset_tool),
        ),
        ToolSpec(
            name=f"{prefix}_list_orders",
            description=(
                "List Coinbase brokerage orders with optional filters. Returns canonical Order models. "
                "When minimal=True, provider metadata is omitted."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": (
                            "Optional Coinbase order status filter (e.g. PENDING, OPEN, FILLED, CANCELLED)."
                        ),
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max number of orders to return (first page only).",
                    },
                    "after": {
                        "type": "string",
                        "description": "Start date/time (RFC3339) to fetch orders from, inclusive.",
                    },
                    "until": {
                        "type": "string",
                        "description": "End date/time (RFC3339) to fetch orders until, exclusive.",
                    },
                    "symbols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of product IDs to filter by (e.g. ['BTC-USD']).",
                    },
                    "side": {
                        "type": "string",
                        "enum": ["buy", "sell"],
                        "description": "Order side filter. Maps to Coinbase BUY/SELL.",
                    },
                },
                "additionalProperties": False,
            },
            handler=tool_handler(_list_orders_tool),
        ),
        ToolSpec(
            name=f"{prefix}_get_order",
            description=(
                "Get a single Coinbase brokerage order by order_id as a canonical Order model. "
                "When minimal=True, provider metadata is omitted."
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
            handler=tool_handler(_get_order_tool),
        ),
    ]
