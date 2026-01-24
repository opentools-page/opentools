from __future__ import annotations

from typing import Tuple

from openai import AsyncOpenAI

from opentools.adapters.models.openai.chat import _run_with_tools_impl
from opentools.core.tool_runner import ToolRunner


async def run_with_tools(
    *,
    client: AsyncOpenAI,
    model: str,
    service: ToolRunner,
    user_prompt: str,
    max_rounds: int = 8,
    max_tokens: int = 600,
    fatal_kinds: Tuple[str, ...] | None = None,
) -> str:
    extra_headers = {}

    return await _run_with_tools_impl(
        client=client,
        model=model,
        service=service,
        user_prompt=user_prompt,
        provider="openrouter",
        max_rounds=max_rounds,
        max_tokens=max_tokens,
        fatal_kinds=fatal_kinds,
        extra_headers=extra_headers or None,
    )
