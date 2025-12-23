from __future__ import annotations

import json
from typing import Any, List

import anthropic
from anthropic import AsyncAnthropic
from anthropic.types import MessageParam
from opentools.core.errors import ProviderError, RateLimitError, ValidationError
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
    if not user_prompt.strip():
        raise ValidationError(
            message="Anthropic user prompt must contain non-whitespace text.",
            domain="llm",
            provider="anthropic",
        )

    messages: List[MessageParam] = [
        {
            "role": "user",
            "content": user_prompt,
        }
    ]

    final_text_chunks: list[str] = []

    for _ in range(max_rounds):
        try:
            resp = await client.messages.create(
                model=model,
                max_tokens=max_tokens,
                tools=service.tools,
                messages=messages,
            )
        except anthropic.RateLimitError as e:
            raise RateLimitError(
                message=str(e),
                domain="llm",
                provider="anthropic",
                status_code=getattr(e, "status_code", None),
                request_id=getattr(e, "request_id", None),
                details=getattr(e, "body", None),
            ) from None
        except anthropic.APIError as e:
            body = getattr(e, "body", None)
            err_type = None
            if isinstance(body, dict):
                err = body.get("error")
                if isinstance(err, dict):
                    err_type = err.get("type")

            if err_type == "invalid_request_error":
                raise ValidationError(
                    message=str(e),
                    domain="llm",
                    provider="anthropic",
                    status_code=getattr(e, "status_code", None),
                    request_id=getattr(e, "request_id", None),
                    details=body,
                ) from None

            raise ProviderError(
                message=str(e),
                domain="llm",
                provider="anthropic",
                status_code=getattr(e, "status_code", None),
                request_id=getattr(e, "request_id", None),
                details=body,
            ) from None
        except Exception as e:
            raise ProviderError(
                message=str(e),
                domain="llm",
                provider="anthropic",
            ) from None

        did_tool = False

        for block in resp.content:
            if block.type == "tool_use":
                did_tool = True

                result = await service.call_tool(block.name, block.input)

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
