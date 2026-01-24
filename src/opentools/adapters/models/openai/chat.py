from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Mapping, Tuple, cast

from openai import APIError, AsyncOpenAI
from openai import RateLimitError as OpenAIRateLimitError
from openai.types.chat import ChatCompletionMessageParam
from opentools.core.errors import ProviderError, RateLimitError
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


async def _run_with_tools_impl(
    *,
    client: AsyncOpenAI,
    model: str,
    service: ToolRunner,
    user_prompt: str,
    provider: str,
    max_rounds: int = 8,
    max_tokens: int = 600,
    fatal_kinds: Tuple[str, ...] | None = None,  # None => use service policy
    extra_headers: Mapping[str, str] | None = None,
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
            resp = await client.chat.completions.create(
                model=model,
                messages=cast(Iterable[ChatCompletionMessageParam], messages),
                tools=service.tools,
                tool_choice="auto",
                max_tokens=max_tokens,
                extra_headers=dict(extra_headers) if extra_headers else None,
            )
        except OpenAIRateLimitError as e:
            raise RateLimitError(
                message=str(e),
                domain="llm",
                provider=provider,
                status_code=getattr(e, "status_code", None),
                request_id=getattr(e, "request_id", None),
                details=getattr(e, "body", None),
            ) from None
        except APIError as e:
            raise ProviderError(
                message=str(e),
                domain="llm",
                provider=provider,
                status_code=getattr(e, "status_code", None),
                request_id=getattr(e, "request_id", None),
                details=getattr(e, "body", None),
            ) from None
        except Exception as e:
            raise ProviderError(
                message=str(e), domain="llm", provider=provider
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
                    if not isinstance(args, dict):
                        result = _tool_validation_error(
                            "Tool arguments must be a JSON object.",
                            details={"tool": name, "raw_args": raw_args},
                        )
                    else:
                        result = await service.call_tool(name, args)
                except json.JSONDecodeError:
                    result = _tool_validation_error(
                        "Invalid JSON in tool arguments.",
                        details={"tool": name, "raw_args": raw_args},
                    )

                raise_if_fatal_tool_error(result, fatal_kinds=resolved_fatal_kinds)

                messages.append(
                    {"role": "tool", "tool_call_id": tc.id, "content": _dump(result)}
                )

            continue

        content = msg.content
        text = (
            content
            if isinstance(content, str)
            else ("" if content is None else str(content))
        )
        if text:
            final_chunks.append(text)
        break

    return "\n".join(final_chunks) if final_chunks else ""


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
    return await _run_with_tools_impl(
        client=client,
        model=model,
        service=service,
        user_prompt=user_prompt,
        provider="openai",
        max_rounds=max_rounds,
        max_tokens=max_tokens,
        fatal_kinds=fatal_kinds,
        extra_headers=None,
    )
