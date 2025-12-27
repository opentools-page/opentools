from __future__ import annotations

from typing import Any, Dict, Iterable, Optional, Protocol, runtime_checkable

from pydantic import BaseModel

from opentools.core.tools import ToolInput, ToolSpec
from pydantic_ai import Tool as PydanticTool


@runtime_checkable
class ToolService(Protocol):
    """Anything that can expose ToolSpecs and run tools."""

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


def _build_description(spec: ToolSpec) -> str:
    """
    Take the base description and append a compact summary of the JSON schema
    so the model actually sees the arguments (limit, cursor, symbols, etc.).
    """
    desc = (spec.description or "").strip()
    schema = getattr(spec, "input_schema", None)

    if not isinstance(schema, dict):
        return desc

    props = schema.get("properties") or {}
    if not props:
        return desc

    lines: list[str] = []
    if desc:
        lines.append(desc)
        lines.append("")

    lines.append("Parameters:")
    for name, prop in props.items():
        t = prop.get("type")
        type_str = t if isinstance(t, str) else "any"

        p_desc = prop.get("description") or ""
        line = f"- {name}"
        if type_str:
            line += f" ({type_str})"
        if p_desc:
            line += f": {p_desc}"
        lines.append(line)

    return "\n".join(lines)


def _make_tool(service: ToolService, spec: ToolSpec) -> PydanticTool:
    safe_name = spec.name
    description = _build_description(spec)

    # No ctx here. The tool just sees validated keyword args.
    async def _fn(**kwargs: Any) -> Any:
        # Strip out None values so you don't spam the provider
        payload = {k: v for k, v in kwargs.items() if v is not None}
        return await service.call_tool(safe_name, payload)

    _fn.__name__ = safe_name
    _fn.__doc__ = description

    return PydanticTool(
        _fn,
        name=safe_name,
        description=description,
    )


def _tools_from_specs(
    service: ToolService, specs: Iterable[ToolSpec]
) -> list[PydanticTool]:
    return [_make_tool(service, spec) for spec in specs]


def tools_for_service(service: ToolService) -> list[PydanticTool]:
    specs = service.tool_specs()
    return _tools_from_specs(service, specs)
