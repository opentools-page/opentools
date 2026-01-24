from __future__ import annotations

import re
from typing import Any, Iterable, Protocol, Tuple, cast, runtime_checkable

from pydantic import BaseModel

from opentools.core.tool_policy import raise_if_fatal_tool_error
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


class _EmptyArgs(BaseModel):
    pass


def _build_description(spec: ToolSpec) -> str:
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


def _py_ident(name: str) -> str:
    s = re.sub(r"[^0-9a-zA-Z_]", "_", name)
    if not s or s[0].isdigit():
        s = f"tool_{s}"
    return s


def _resolve_fatal_kinds(
    service: ToolService, fatal_kinds: Tuple[str, ...] | None
) -> Tuple[str, ...]:
    if fatal_kinds is not None:
        return fatal_kinds
    return cast(
        Tuple[str, ...],
        getattr(service, "fatal_tool_error_kinds", ("auth", "config")),
    )


def _make_tool(
    service: ToolService,
    spec: ToolSpec,
    *,
    fatal_kinds: Tuple[str, ...] | None = None,
) -> PydanticTool:
    safe_name = spec.name
    description = _build_description(spec)
    resolved_fatal_kinds = _resolve_fatal_kinds(service, fatal_kinds)

    async def _fn(**kwargs: Any) -> Any:
        payload = {k: v for k, v in kwargs.items() if v is not None}
        result = await service.call_tool(safe_name, payload)
        raise_if_fatal_tool_error(result, fatal_kinds=resolved_fatal_kinds)
        return result

    _fn.__name__ = _py_ident(safe_name)
    _fn.__doc__ = description

    return PydanticTool(
        _fn,
        name=safe_name,
        description=description,
    )


def _tools_from_specs(
    service: ToolService,
    specs: Iterable[ToolSpec],
    *,
    fatal_kinds: Tuple[str, ...] | None = None,
) -> list[PydanticTool]:
    return [_make_tool(service, spec, fatal_kinds=fatal_kinds) for spec in specs]


def tools_for_service(
    service: ToolService,
    *,
    fatal_kinds: Tuple[str, ...] | None = None,
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
) -> list[PydanticTool]:
    specs = service.tool_specs(include=include, exclude=exclude)
    return _tools_from_specs(service, specs, fatal_kinds=fatal_kinds)
