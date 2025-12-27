from __future__ import annotations

from typing import Any, Iterable, Protocol

from .tools import ToolInput, ToolSpec
from .types import FrameworkName


class FrameworkService(Protocol):
    framework: FrameworkName | None

    def tool_specs(
        self,
        *,
        include: Iterable[str] | None = None,
        exclude: Iterable[str] | None = None,
    ) -> list[ToolSpec]: ...

    async def call_tool(self, tool_name: str, tool_input: ToolInput) -> Any: ...

    @property
    def tools(self) -> list[Any]: ...


def framework_tools(service: FrameworkService) -> list[Any]:
    # no framework configured, return model-shaped tools
    if service.framework is None:
        return list(service.tools)

    if service.framework == "pydantic_ai":
        from opentools.adapters.frameworks.pydantic_ai import tools_for_service

        return tools_for_service(service)

    if service.framework == "langgraph":
        from opentools.adapters.frameworks.langgraph import (
            tools_for_service as lg_tools_for_service,
        )

        return lg_tools_for_service(service)

    raise ValueError(f"Unknown framework: {service.framework!r}")
