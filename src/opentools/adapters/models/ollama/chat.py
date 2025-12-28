from __future__ import annotations

import json
from typing import Any, List

from ollama import AsyncClient, ResponseError
from opentools.core.errors import ProviderError, TransientError
from opentools.core.tool_runner import ToolRunner


def _dump(x: Any) -> str:
    return json.dumps(x, indent=2, default=str)


async def run_with_tools(
    *,
    client: AsyncClient,
    model: str,
    service: ToolRunner,
    user_prompt: str,
    max_rounds: int = 8,
) -> str:
    messages: List[Any] = [{"role": "user", "content": user_prompt}]
    final_chunks: list[str] = []

    for _ in range(max_rounds):
        try:
            resp: Any = await client.chat(
                model=model,
                messages=messages,
                tools=service.tools,
                stream=False,
            )
        except ResponseError as exc:
            raise ProviderError(
                message=str(exc),
                domain="llm",
                provider="ollama",
                status_code=getattr(exc, "status_code", None),
                details=getattr(exc, "error", None),
            ) from None
        except (ConnectionError, OSError) as exc:
            raise TransientError(
                message=(
                    "Failed to reach Ollama host. "
                    "Check that `host` points to an Ollama server "
                    "and that it is running."
                ),
                domain="llm",
                provider="ollama",
                details=str(exc),
            ) from None

        except Exception as exc:
            raise ProviderError(
                message=str(exc),
                domain="llm",
                provider="ollama",
            ) from None

        message = getattr(resp, "message", None) or resp.get("message")
        if message is None:
            raise ProviderError(
                message="Ollama chat response missing 'message'",
                domain="llm",
                provider="ollama",
                details=repr(resp),
            )

        messages.append(message)

        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls is None:
            tool_calls = getattr(message, "tool_calls", None)
        if tool_calls is None and isinstance(message, dict):
            tool_calls = message.get("tool_calls")

        tool_calls = tool_calls or []

        if tool_calls:
            for tc in tool_calls:
                func = getattr(tc, "function", None)

                if func is None and isinstance(tc, dict):
                    func = tc.get("function")

                if func is None:
                    continue

                name = getattr(func, "name", None)
                if name is None and isinstance(func, dict):
                    name = func.get("name")

                if not name:
                    continue

                raw_args = getattr(func, "arguments", None)
                if raw_args is None and isinstance(func, dict):
                    raw_args = func.get("arguments")

                if isinstance(raw_args, str):
                    try:
                        args = json.loads(raw_args)
                    except Exception:
                        args = {}
                elif isinstance(raw_args, dict):
                    args = raw_args
                else:
                    args = {}

                result = await service.call_tool(name, args)

                messages.append(
                    {
                        "role": "tool",
                        "tool_name": name,
                        "content": _dump(result),
                    }
                )

            continue

        content = getattr(message, "content", None)
        if content is None and isinstance(message, dict):
            content = message.get("content")

        if content:
            final_chunks.append(str(content))
        break

    return "\n".join(final_chunks) if final_chunks else ""
