from __future__ import annotations

from opentools.core.tools import ToolSpec, tool_handler


def coinbase_tools(service) -> list[ToolSpec]:
    return [
        ToolSpec(
            name="get_account",
            description=(
                "Get Coinbase account info (using the primary brokerage account). "
                "Includes currency and balances in a canonical Account model."
            ),
            input_schema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            handler=tool_handler(service.get_account),
        ),
    ]
