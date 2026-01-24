from __future__ import annotations

import json
from typing import Any, List, Tuple, cast

import google.genai as genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types

from opentools.core.errors import (
    AuthError,
    NotFoundError,
    OpenToolsError,
    ProviderError,
    RateLimitError,
    TransientError,
)
from opentools.core.tool_policy import raise_if_fatal_tool_error
from opentools.core.tool_runner import ToolRunner


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


def _jsonable(x: Any) -> Any:
    try:
        return json.loads(json.dumps(x, default=str))
    except Exception:
        return {"_unserializable": True, "repr": repr(x)}


def _wrap_gemini_error(exc: genai_errors.APIError) -> OpenToolsError:
    code = getattr(exc, "code", None)
    message = getattr(exc, "message", str(exc))

    base_kwargs = {
        "message": message,
        "domain": "llm",
        "provider": "gemini",
        "status_code": code if isinstance(code, int) else None,
        "details": {"raw": str(exc)},
    }

    if code == 429:
        return RateLimitError(**base_kwargs)
    if code in (401, 403):
        return AuthError(**base_kwargs)
    if code == 404:
        return NotFoundError(**base_kwargs)
    if isinstance(code, int) and code >= 500:
        return TransientError(**base_kwargs)
    return ProviderError(**base_kwargs)


async def run_with_tools(
    *,
    client: genai.Client,
    model: str,
    service: ToolRunner,
    user_prompt: str,
    max_rounds: int = 8,
    max_output_tokens: int = 600,
    fatal_kinds: Tuple[str, ...] | None = None,
) -> str:
    aclient = client.aio

    resolved_fatal_kinds: Tuple[str, ...] = (
        fatal_kinds
        if fatal_kinds is not None
        else cast(
            Tuple[str, ...],
            getattr(service, "fatal_tool_error_kinds", ("auth", "config")),
        )
    )

    contents: List[genai_types.Content] = [
        genai_types.Content(
            role="user",
            parts=[genai_types.Part.from_text(text=user_prompt)],
        )
    ]

    final_chunks: list[str] = []

    for _ in range(max_rounds):
        try:
            response = await aclient.models.generate_content(
                model=model,
                contents=contents,
                config=genai_types.GenerateContentConfig(
                    tools=service.tools,
                    automatic_function_calling=genai_types.AutomaticFunctionCallingConfig(
                        disable=True
                    ),
                    max_output_tokens=max_output_tokens,
                ),
            )
        except genai_errors.APIError as exc:
            raise _wrap_gemini_error(exc) from None
        except Exception as exc:
            raise ProviderError(
                message=str(exc),
                domain="llm",
                provider="gemini",
            ) from None

        function_calls_raw = getattr(response, "function_calls", None)
        function_calls: list[Any] = list(function_calls_raw or [])

        if function_calls:
            candidates = getattr(response, "candidates", None)
            if isinstance(candidates, list) and len(candidates) > 0:
                first_candidate = candidates[0]
                cand_content = getattr(first_candidate, "content", None)
                if cand_content is not None:
                    contents.append(cast(genai_types.Content, cand_content))

            for fc_any in function_calls:
                fc = cast(Any, fc_any)

                name = getattr(fc, "name", None)
                if not isinstance(name, str) or not name:
                    continue

                func_call = getattr(fc, "function_call", None)
                raw_args_obj = (
                    getattr(func_call, "args", {}) if func_call is not None else {}
                )

                if isinstance(raw_args_obj, dict):
                    args: Any = raw_args_obj
                else:
                    try:
                        args = dict(raw_args_obj)  # type: ignore[arg-type]
                    except Exception:
                        args = {}

                if not isinstance(args, dict):
                    result = _tool_validation_error(
                        "Tool arguments must be a JSON object.",
                        details={"tool": name, "raw_args": repr(raw_args_obj)},
                    )
                else:
                    result = await service.call_tool(name, args)

                raise_if_fatal_tool_error(result, fatal_kinds=resolved_fatal_kinds)

                function_response_part = genai_types.Part.from_function_response(
                    name=name,
                    response={"result": _jsonable(result)},
                )

                contents.append(
                    genai_types.Content(
                        role="tool",
                        parts=[function_response_part],
                    )
                )

            continue

        text = getattr(response, "text", None) or ""
        if text:
            final_chunks.append(text)
        break

    return "\n".join(final_chunks) if final_chunks else ""
