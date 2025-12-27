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
                "(accounts, has_next, cursor, size)."
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
    ]
