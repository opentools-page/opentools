from __future__ import annotations

from typing import (
    Any,
    Dict,
    Iterable,
    Optional,
    Protocol,
    Tuple,
    cast,
    runtime_checkable,
)

from pydantic import BaseModel, create_model

from opentools.core.tool_policy import raise_if_fatal_tool_error
from opentools.core.tools import ToolInput, ToolSpec

try:
    from langchain_core.tools import StructuredTool
except ImportError:
    from langchain.tools import StructuredTool  # type: ignore[assignment]


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


def _resolve_fatal_kinds(
    service: ToolService, fatal_kinds: Tuple[str, ...] | None
) -> Tuple[str, ...]:
    if fatal_kinds is not None:
        return fatal_kinds
    return cast(
        Tuple[str, ...],
        getattr(service, "fatal_tool_error_kinds", ("auth", "config")),
    )


def _json_schema_to_model(name: str, schema: Dict[str, Any]) -> type[BaseModel]:
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


def _make_langchain_tool(
    service: ToolService,
    spec: ToolSpec,
    *,
    fatal_kinds: Tuple[str, ...] | None = None,
) -> Any:
    safe_name = spec.name
    description = spec.description or ""
    resolved_fatal_kinds = _resolve_fatal_kinds(service, fatal_kinds)

    schema = getattr(spec, "input_schema", None)
    ArgsModel = (
        _json_schema_to_model(f"{safe_name}_Args", schema)
        if isinstance(schema, dict)
        else _EmptyArgs
    )

    async def _fn_async(**kwargs: Any) -> Any:
        payload = {k: v for k, v in kwargs.items() if v is not None}
        result = await service.call_tool(safe_name, payload)
        raise_if_fatal_tool_error(result, fatal_kinds=resolved_fatal_kinds)
        return result

    def _fn_sync(**kwargs: Any) -> Any:
        raise RuntimeError(
            "This tool is async-only. Use it in an async LangGraph/LangChain runtime."
        )

    _fn_async.__name__ = safe_name
    _fn_async.__doc__ = description
    _fn_sync.__name__ = safe_name
    _fn_sync.__doc__ = description

    return StructuredTool(
        name=safe_name,
        description=description,
        func=_fn_sync,
        coroutine=_fn_async,
        args_schema=ArgsModel,
    )


def tools_for_service(
    service: ToolService,
    *,
    fatal_kinds: Tuple[str, ...] | None = None,
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
) -> list[Any]:
    specs = service.tool_specs(include=include, exclude=exclude)
    return [
        _make_langchain_tool(service, spec, fatal_kinds=fatal_kinds) for spec in specs
    ]
