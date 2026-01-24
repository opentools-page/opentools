from __future__ import annotations

import json
from typing import Any, List, Tuple, cast

import anthropic
from anthropic import AsyncAnthropic
from anthropic.types import MessageParam
from opentools.core.errors import (
    AuthError,
    NotFoundError,
    OpenToolsError,
    ProviderError,
    RateLimitError,
    TransientError,
    ValidationError,
)
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


def _wrap_anthropic_error(exc: Exception) -> OpenToolsError:
    status = getattr(exc, "status_code", None)
    request_id = getattr(exc, "request_id", None)
    body = getattr(exc, "body", None)

    base_kwargs = {
        "message": str(exc),
        "domain": "llm",
        "provider": "anthropic",
        "status_code": status if isinstance(status, int) else None,
        "request_id": request_id if isinstance(request_id, str) else None,
        "details": body,
    }

    if isinstance(exc, anthropic.RateLimitError) or status == 429:
        return RateLimitError(**base_kwargs)
    if isinstance(exc, anthropic.AuthenticationError) or status in (401, 403):
        return AuthError(**base_kwargs)
    if isinstance(exc, anthropic.NotFoundError) or status == 404:
        return NotFoundError(**base_kwargs)
    if isinstance(status, int) and status >= 500:
        return TransientError(**base_kwargs)

    if isinstance(exc, anthropic.BadRequestError):
        return ValidationError(**base_kwargs)

    return ProviderError(**base_kwargs)


async def run_with_tools(
    *,
    client: AsyncAnthropic,
    model: str,
    service: ToolRunner,
    user_prompt: str,
    max_rounds: int = 8,
    max_tokens: int = 600,
    fatal_kinds: Tuple[str, ...] | None = None,
) -> str:
    if not user_prompt.strip():
        raise ValidationError(
            message="Anthropic user prompt must contain non-whitespace text.",
            domain="llm",
            provider="anthropic",
        )

    resolved_fatal_kinds: Tuple[str, ...] = (
        fatal_kinds
        if fatal_kinds is not None
        else cast(
            Tuple[str, ...],
            getattr(service, "fatal_tool_error_kinds", ("auth", "config")),
        )
    )

    messages: List[MessageParam] = [{"role": "user", "content": user_prompt}]
    final_text_chunks: list[str] = []

    for _ in range(max_rounds):
        try:
            resp = await client.messages.create(
                model=model,
                max_tokens=max_tokens,
                tools=service.tools,
                messages=messages,
            )
        except Exception as exc:
            raise _wrap_anthropic_error(exc) from None

        tool_uses: list[Any] = []
        text_chunks: list[str] = []

        for block in resp.content:
            if getattr(block, "type", None) == "tool_use":
                tool_uses.append(block)
            elif getattr(block, "type", None) == "text":
                text_chunks.append(getattr(block, "text", "") or "")

        if text_chunks:
            final_text_chunks.extend([t for t in text_chunks if t])

        if not tool_uses:
            break

        messages.append({"role": "assistant", "content": list(resp.content)})

        for block in tool_uses:
            name = getattr(block, "name", None)
            tool_use_id = getattr(block, "id", None)
            tool_input = getattr(block, "input", None)

            if not isinstance(name, str) or not name:
                continue
            if not isinstance(tool_use_id, str) or not tool_use_id:
                continue

            if not isinstance(tool_input, dict):
                result: Any = _tool_validation_error(
                    "Tool arguments must be a JSON object.",
                    details={"tool": name, "raw_args": repr(tool_input)},
                )
            else:
                result = await service.call_tool(name, tool_input)

            raise_if_fatal_tool_error(result, fatal_kinds=resolved_fatal_kinds)

            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": _dump(result),
                        }
                    ],
                }
            )

    return "\n".join([t for t in final_text_chunks if t]).strip()
