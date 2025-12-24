from __future__ import annotations

from typing import Any, Iterable, Protocol, runtime_checkable

from pydantic import BaseModel

from opentools.core.tools import ToolInput, ToolSpec

try:
    # current LC
    from langchain_core.tools import StructuredTool
except ImportError:  # pragma: no cover
    # older layout
    from langchain.tools import StructuredTool  # type: ignore[assignment]


@runtime_checkable
class ToolService(Protocol):
    """
    Generic surface for anything that can be projected into LangGraph tools.
    """

    def tool_specs(
        self,
        *,
        include: Iterable[str] | None = None,
        exclude: Iterable[str] | None = None,
    ) -> list[ToolSpec]: ...

    async def call_tool(self, tool_name: str, tool_input: ToolInput) -> Any: ...


class _EmptyArgs(BaseModel):
    """Tool takes no arguments."""

    pass


def _make_langgraph_tool(service: ToolService, spec: ToolSpec) -> Any:
    """
    Turn a single ToolSpec into a LangChain / LangGraph StructuredTool.

    - Uses the OpenTools handler via `service.call_tool`.
    - Exposes the canonical Pydantic schema from `spec.input_schema`.
    """
    safe_name = spec.name
    description = spec.description or ""
    args_schema = getattr(spec, "input_schema", None) or _EmptyArgs

    async def _fn(**kwargs: Any) -> Any:
        # kwargs is already the parsed dict matching args_schema
        return await service.call_tool(safe_name, kwargs)

    _fn.__name__ = safe_name
    _fn.__doc__ = description

    tool = StructuredTool(
        name=safe_name,
        description=description,
        coroutine=_fn,  # async handler
        func=None,  # no sync version
        args_schema=args_schema,
    )

    return tool


def _tools_from_specs(service: ToolService, specs: Iterable[ToolSpec]) -> list[Any]:
    return [_make_langgraph_tool(service, spec) for spec in specs]


def tools_for_service(service: ToolService) -> list[Any]:
    """
    Public entrypoint used by core.frameworks.framework_tools.
    """
    specs = service.tool_specs()
    return _tools_from_specs(service, specs)
