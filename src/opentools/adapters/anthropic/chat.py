from __future__ import annotations

import json
from typing import Any, List

from anthropic import AsyncAnthropic
from anthropic.types import MessageParam
from opentools.core.tool_runner import ToolRunner


def _dump(x: Any) -> str:
    return json.dumps(x, indent=2, default=str)


async def run_with_tools(
    *,
    client: AsyncAnthropic,
    model: str,
    service: ToolRunner,
    user_prompt: str,
    max_rounds: int = 8,
    max_tokens: int = 600,
) -> str:
    """
    High-level Anthropic tool loop.

    - Sends initial user prompt
    - Lets the model request tools
    - Executes tools via `service.call_tool`
    - Feeds tool_result blocks back
    - Returns final text answer (all text chunks joined by newlines)
    """

    messages: List[MessageParam] = [
        {
            "role": "user",
            "content": user_prompt,
        }
    ]

    final_text_chunks: list[str] = []

    for _ in range(max_rounds):
        resp = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            tools=service.tools,
            messages=messages,
        )

        did_tool = False

        for block in resp.content:
            if block.type == "tool_use":
                did_tool = True

                # Execute via SDK
                result = await service.call_tool(block.name, block.input)

                # Echo tool_use block back
                messages.append({"role": "assistant", "content": [block]})
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": _dump(result),
                            }
                        ],
                    }
                )

            elif block.type == "text":
                final_text_chunks.append(block.text)

        if not did_tool:
            break

    return "\n".join(final_text_chunks) if final_text_chunks else ""
