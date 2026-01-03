from __future__ import annotations

from typing import Dict, List

from google.genai import types as genai_types

from opentools.adapters.utils import sanitise_tool_name, unique_name
from opentools.core.tools import ToolBundle, ToolSpec


def to_gemini_bundle(tool_specs: List[ToolSpec]) -> ToolBundle:
    dispatch: Dict[str, ToolSpec] = {}
    used: set[str] = set()
    function_decls: List[genai_types.FunctionDeclaration] = []

    for spec in tool_specs:
        base = sanitise_tool_name(spec.name)
        safe = unique_name(base, used)

        dispatch[safe] = spec

        fn = genai_types.FunctionDeclaration(
            name=safe,
            description=spec.description,
            parameters_json_schema=spec.input_schema,
        )
        function_decls.append(fn)

    tools: List[genai_types.Tool] = []
    if function_decls:
        tools.append(genai_types.Tool(function_declarations=function_decls))

    return ToolBundle(tools=tools, dispatch=dispatch)
