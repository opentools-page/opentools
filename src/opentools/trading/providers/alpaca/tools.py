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
            description="Get Alpaca trading clock (open/closed and next open/close).",
            input_schema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            handler=tool_handler(service.get_clock),
        ),
    ]
