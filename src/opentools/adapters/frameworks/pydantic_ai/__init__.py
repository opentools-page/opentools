from __future__ import annotations

from typing import Any, Iterable, Protocol, runtime_checkable

from opentools.core.tools import ToolInput, ToolSpec
from pydantic_ai import Tool as PydanticTool


@runtime_checkable
class ToolService(Protocol):
    def tool_specs(
        self,
        *,
        include: Iterable[str] | None = None,
        exclude: Iterable[str] | None = None,
    ) -> list[ToolSpec]: ...

    async def call_tool(self, tool_name: str, tool_input: ToolInput) -> Any: ...


def _tools_from_specs(
    service: ToolService, specs: Iterable[ToolSpec]
) -> list[PydanticTool]:
    tools: list[PydanticTool] = []

    for spec in specs:
        safe_name = spec.name
        description = spec.description

        async def _fn(
            ctx,  # type: ignore[unused-argument]
            _tool_name: str = safe_name,
            **kwargs: Any,
        ) -> Any:
            return await service.call_tool(_tool_name, kwargs)

        _fn.__name__ = safe_name
        _fn.__doc__ = description

        tools.append(
            PydanticTool(
                _fn,
                name=safe_name,
                description=description,
            )
        )

    return tools


def tools_for_service(service: ToolService) -> list[PydanticTool]:
    specs = service.tool_specs()
    return _tools_from_specs(service, specs)
