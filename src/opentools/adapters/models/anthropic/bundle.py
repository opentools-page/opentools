from __future__ import annotations

from typing import Dict, List

from anthropic.types import ToolParam
from opentools.adapters.utils import sanitise_tool_name, unique_name
from opentools.core.tools import ToolBundle, ToolSpec


def to_anthropic_bundle(tool_specs: List[ToolSpec]) -> ToolBundle:
    tools: List[ToolParam] = []
    dispatch: Dict[str, ToolSpec] = {}
    used: set[str] = set()

    for spec in tool_specs:
        base = sanitise_tool_name(spec.name)
        safe = unique_name(base, used)

        dispatch[safe] = spec
        tools.append(
            {
                "name": safe,
                "description": spec.description,
                "input_schema": spec.input_schema,
            }
        )

    return ToolBundle(tools=tools, dispatch=dispatch)
