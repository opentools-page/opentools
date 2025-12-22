from __future__ import annotations

from typing import Dict, List, Sequence

from opentools.adapters.utils import sanitize_tool_name, unique_name
from opentools.core.tools import ToolBundle, ToolSpec


def to_openai_bundle(tool_specs: Sequence[ToolSpec]) -> ToolBundle:
    functions: List[dict] = []
    dispatch: Dict[str, ToolSpec] = {}
    used: set[str] = set()

    for spec in tool_specs:
        base = sanitize_tool_name(spec.name)
        safe = unique_name(base, used)

        dispatch[safe] = spec
        functions.append(
            {
                "name": safe,
                "description": spec.description,
                "parameters": spec.input_schema,
            }
        )

    return ToolBundle(tools=functions, dispatch=dispatch)
