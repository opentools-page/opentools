from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, cast

from openai import APIError, AsyncOpenAI
from openai import RateLimitError as OpenAIRateLimitError
from openai.types.chat import ChatCompletionMessageParam
from opentools.core.errors import ProviderError, RateLimitError
from opentools.core.tool_runner import ToolRunner


def _dump(x: Any) -> str:
    return json.dumps(x, indent=2, default=str)


async def run_with_tools(
    *,
    client: AsyncOpenAI,
    model: str,
    service: ToolRunner,
    user_prompt: str,
    max_rounds: int = 8,
    max_tokens: int = 600,
) -> str:
    messages: List[Dict[str, Any]] = [
        {"role": "user", "content": user_prompt},
    ]

    final_chunks: list[str] = []

    for _ in range(max_rounds):
        try:
            resp = await client.chat.completions.create(
                model=model,
                messages=cast(Iterable[ChatCompletionMessageParam], messages),
                tools=service.tools,
                tool_choice="auto",
                max_tokens=max_tokens,
            )
        except OpenAIRateLimitError as e:
            raise RateLimitError(
                message=str(e),
                domain="llm",
                provider="openai",
                status_code=getattr(e, "status_code", None),
                request_id=getattr(e, "request_id", None),
                details=getattr(e, "body", None),
            ) from None
        except APIError as e:
            raise ProviderError(
                message=str(e),
                domain="llm",
                provider="openai",
                status_code=getattr(e, "status_code", None),
                request_id=getattr(e, "request_id", None),
                details=getattr(e, "body", None),
            ) from None
        except Exception as e:
            raise ProviderError(
                message=str(e),
                domain="llm",
                provider="openai",
            ) from None

        msg = resp.choices[0].message
        tool_calls = msg.tool_calls or []

        if tool_calls:
            messages.append(
                {
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [tc.model_dump() for tc in tool_calls],
                }
            )

            for tc in tool_calls:
                func = getattr(tc, "function", None)
                if func is None:
                    continue

                name = func.name
                raw_args = func.arguments or "{}"
                try:
                    args = json.loads(raw_args)
                except Exception:
                    args = {}

                result = await service.call_tool(name, args)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": _dump(result),
                    }
                )

            continue

        content = msg.content
        if content is None:
            text = ""
        elif isinstance(content, str):
            text = content
        else:
            text = str(content)

        if text:
            final_chunks.append(text)
        break

    return "\n".join(final_chunks) if final_chunks else ""
