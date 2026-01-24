from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple, cast

from ollama import AsyncClient, ResponseError
from opentools.core.errors import ProviderError, TransientError
from opentools.core.tool_policy import raise_if_fatal_tool_error
from opentools.core.tool_runner import ToolRunner


def _dump(x: Any) -> str:
    return json.dumps(x, indent=2, default=str)


def _tool_validation_error(
    message: str, *, details: Any | None = None
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "ok": False,
        "error": {"kind": "validation", "message": message},
    }
    if details is not None:
        out["error"]["details"] = details
    return out


def _as_dict(x: Any) -> dict[str, Any] | None:
    return x if isinstance(x, dict) else None


def _get(obj: Any, key: str, default: Any = None) -> Any:
    """
    Safely access either dict-like or object-like values.
    """
    d = _as_dict(obj)
    if d is not None:
        return d.get(key, default)
    return getattr(obj, key, default)


async def run_with_tools(
    *,
    client: AsyncClient,
    model: str,
    service: ToolRunner,
    user_prompt: str,
    max_rounds: int = 8,
    fatal_kinds: Tuple[str, ...] | None = None,  # service policy
) -> str:
    messages: List[Dict[str, Any]] = [{"role": "user", "content": user_prompt}]
    final_chunks: list[str] = []

    resolved_fatal_kinds: Tuple[str, ...] = (
        fatal_kinds
        if fatal_kinds is not None
        else cast(
            Tuple[str, ...],
            getattr(service, "fatal_tool_error_kinds", ("auth", "config")),
        )
    )

    for _ in range(max_rounds):
        try:
            resp: Any = await client.chat(
                model=model,
                messages=messages,
                tools=service.tools,
                stream=False,
            )
        except ResponseError as e:
            raise ProviderError(
                message=str(e),
                domain="llm",
                provider="ollama",
                status_code=getattr(e, "status_code", None),
                details=getattr(e, "error", None),
            ) from None
        except (ConnectionError, OSError) as e:
            raise TransientError(
                message="Failed to reach Ollama host. Is the Ollama server running?",
                domain="llm",
                provider="ollama",
                details=str(e),
            ) from None
        except Exception as e:
            raise ProviderError(
                message=str(e), domain="llm", provider="ollama"
            ) from None

        message = _get(resp, "message")
        if message is None:
            raise ProviderError(
                message="Ollama chat response missing 'message'",
                domain="llm",
                provider="ollama",
                details=repr(resp),
            )

        role = _get(message, "role", "assistant")
        content = _get(message, "content", "") or ""
        tool_calls = _get(message, "tool_calls", []) or []

        assistant_msg: Dict[str, Any] = {
            "role": role or "assistant",
            "content": content,
        }
        if tool_calls:
            assistant_msg["tool_calls"] = tool_calls
        messages.append(assistant_msg)

        if tool_calls:
            for tc in tool_calls:
                func = _get(tc, "function")
                if func is None:
                    continue

                name = _get(func, "name")
                if not name:
                    continue

                raw_args = _get(func, "arguments")

                if isinstance(raw_args, dict):
                    args: Any = raw_args
                elif isinstance(raw_args, str):
                    try:
                        args = json.loads(raw_args)
                    except json.JSONDecodeError:
                        args = _tool_validation_error(
                            "Invalid JSON in tool arguments.",
                            details={"tool": name, "raw_args": raw_args},
                        )
                else:
                    args = {}

                if isinstance(args, dict):
                    result = await service.call_tool(name, args)
                else:
                    result = _tool_validation_error(
                        "Tool arguments must be a JSON object.",
                        details={"tool": name, "raw_args": raw_args},
                    )

                raise_if_fatal_tool_error(result, fatal_kinds=resolved_fatal_kinds)
                messages.append(
                    {
                        "role": "tool",
                        "name": name,
                        "content": _dump(result),
                    }
                )

            continue

        if content:
            final_chunks.append(str(content))
        break

    return "\n".join(final_chunks) if final_chunks else ""
