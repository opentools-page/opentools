from __future__ import annotations

import asyncio
from typing import Any, Dict, Iterable, Optional, Protocol, runtime_checkable

from pydantic import BaseModel, create_model

from opentools.core.tools import ToolInput, ToolSpec

try:
    # current
    from langchain_core.tools import StructuredTool
except ImportError:
    # older
    from langchain.tools import StructuredTool  # type: ignore[assignment]


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


def _json_schema_to_model(name: str, schema: Dict[str, Any]) -> type[BaseModel]:
    """
    Minimal JSON-schema -> Pydantic model adapter.

    Supports:
      - type: object
      - properties + required
      - basic types: string, integer, number, boolean, array, object

    Ignores:
      - additionalProperties
      - oneOf / anyOf / enum / etc.
    """
    if schema.get("type") != "object":
        return _EmptyArgs

    props: Dict[str, Any] = schema.get("properties", {}) or {}
    required = set(schema.get("required", []))

    fields: Dict[str, tuple[Any, Any]] = {}

    for field_name, prop in props.items():
        t = prop.get("type", "string")
        py_type: Any

        if t == "integer":
            py_type = int
        elif t == "number":
            py_type = float
        elif t == "boolean":
            py_type = bool
        elif t == "array":
            # Best-effort: look at items.type, default to str
            items_schema = prop.get("items") or {}
            item_type_str = items_schema.get("type", "string")

            if item_type_str == "integer":
                item_py_type = int
            elif item_type_str == "number":
                item_py_type = float
            elif item_type_str == "boolean":
                item_py_type = bool
            elif item_type_str == "object":
                item_py_type = Dict[str, Any]
            else:
                item_py_type = str

            py_type = list[item_py_type]  # type: ignore[index]
        elif t == "object":
            py_type = Dict[str, Any]
        else:
            py_type = str

        if field_name in required:
            fields[field_name] = (py_type, ...)
        else:
            fields[field_name] = (Optional[py_type], None)

    return create_model(name, **fields)  # type: ignore[arg-type]


def _make_langgraph_tool(service: ToolService, spec: ToolSpec) -> Any:
    safe_name = spec.name
    description = spec.description or ""

    schema = getattr(spec, "input_schema", None)
    if isinstance(schema, dict):
        ArgsModel = _json_schema_to_model(f"{safe_name}_Args", schema)
    else:
        ArgsModel = _EmptyArgs

    # async implementation (real one)
    async def _fn_async(**kwargs: Any) -> Any:
        return await service.call_tool(safe_name, kwargs)

    # sync wrapper so ToolNode can call .invoke()
    def _fn_sync(**kwargs: Any) -> Any:
        return asyncio.run(service.call_tool(safe_name, kwargs))

    _fn_async.__name__ = safe_name
    _fn_async.__doc__ = description
    _fn_sync.__name__ = safe_name
    _fn_sync.__doc__ = description

    tool = StructuredTool(
        name=safe_name,
        description=description,
        func=_fn_sync,  # sync path (ToolNode _execute_tool_sync)
        coroutine=_fn_async,  # async path if you ever use ainvoke
        args_schema=ArgsModel,
    )

    return tool


def _tools_from_specs(service: ToolService, specs: Iterable[ToolSpec]) -> list[Any]:
    return [_make_langgraph_tool(service, spec) for spec in specs]


def tools_for_service(service: ToolService) -> list[Any]:
    specs = service.tool_specs()
    return _tools_from_specs(service, specs)
