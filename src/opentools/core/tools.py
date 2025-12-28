from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from .errors import OpenToolsError

ToolInput = dict[str, Any]
ToolHandler = Callable[[ToolInput], Awaitable[Any]]


@dataclass(frozen=True)
class ToolSpec:
    """
    Neutral description of a tool.

    - name: internal canonical name
    - description: brief context of the tool
    - input_schema: dictionary
    """

    name: str
    description: str
    input_schema: dict[str, Any]
    handler: ToolHandler


@dataclass
class ToolBundle:
    """
    Provider-shaped tools + dispatch table.

    - tools: list of provider-specific tool objects (Anthropic/OpenAI/etc)
    - dispatch: map from sanitized tool name -> ToolSpec
    """

    tools: list[Any]
    dispatch: dict[str, ToolSpec]

    async def call(self, tool_name: str, tool_input: ToolInput) -> Any:
        """
        Run a tool by its sanitized name (the one the model sees).
        """
        spec = self.dispatch.get(tool_name)
        if spec is None:
            return {
                "ok": False,
                "error": {
                    "kind": "validation",
                    "message": f"Unknown tool: {tool_name}",
                },
            }
        return await spec.handler(tool_input)


def merge_bundles(*bundles: ToolBundle) -> ToolBundle:
    """
    Combine multiple ToolBundles into a single one.

    - concatenates provider-ready `tools` lists
    - merges dispatch maps
    - raises on name collisions (sanitized names must be unique)
    """
    tools: list[Any] = []
    dispatch: dict[str, ToolSpec] = {}

    for b in bundles:
        tools.extend(b.tools)
        for name, spec in b.dispatch.items():
            if name in dispatch:
                raise ValueError(f"Duplicate tool name in merged bundles: {name}")
            dispatch[name] = spec

    return ToolBundle(tools=tools, dispatch=dispatch)


def error_payload(e: OpenToolsError) -> dict[str, Any]:
    return {
        "kind": e.kind,
        "message": e.message,
        "domain": e.domain,
        "provider": e.provider,
        "status_code": e.status_code,
        "request_id": e.request_id,
        "details": e.details,
        "missing_scopes": getattr(e, "missing_scopes", None),
        "retry_after_s": getattr(e, "retry_after_s", None),
        "resource_type": getattr(e, "resource_type", None),
        "resource_id": getattr(e, "resource_id", None),
        "field_errors": getattr(e, "field_errors", None),
    }


def tool_handler(fn: Callable[..., Awaitable[Any]]) -> ToolHandler:
    """
    Wrap a domain method so it always returns:

      {"ok": True, "data": ...}
      {"ok": False, "error": ...}

    This keeps tool outputs consistent for agents.
    """

    async def _wrapped(inp: ToolInput) -> dict[str, Any]:
        try:
            data = await fn(**inp)
            return {"ok": True, "data": data}
        except OpenToolsError as e:
            return {"ok": False, "error": error_payload(e)}

    return _wrapped
