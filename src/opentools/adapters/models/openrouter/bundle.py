from __future__ import annotations

from typing import List

from opentools.adapters.models.openai.bundle import to_openai_bundle
from opentools.core.tools import ToolBundle, ToolSpec


def to_openrouter_bundle(tool_specs: List[ToolSpec]) -> ToolBundle:
    # open-ai compatible so reusing
    return to_openai_bundle(tool_specs)
