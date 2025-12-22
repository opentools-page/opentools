from __future__ import annotations

from typing import Any, Protocol

from .tools import ToolInput


class ToolRunner(Protocol):
    """
    Minimal surface needed by chat adapters:

    - .tools: provider-shaped tools list (what goes into tools=)
    - .call_tool(name, input): execute a tool by sanitized name
    """

    @property
    def tools(self) -> list[Any]: ...
    async def call_tool(self, tool_name: str, tool_input: ToolInput) -> Any: ...
