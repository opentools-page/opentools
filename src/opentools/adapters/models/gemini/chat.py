from __future__ import annotations

from typing import Any, List, cast

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
from opentools.core.tool_runner import ToolRunner


def _wrap_gemini_error(exc: genai_errors.APIError) -> OpenToolsError:
    """
    Map google-genai APIError -> our OpenTools error types.
    """
    code = getattr(exc, "code", None)
    message = getattr(exc, "message", str(exc))

    base_kwargs = {
        "message": message,
        "domain": "llm",
        "provider": "gemini",
        "status_code": code,
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
) -> str:
    aclient = client.aio

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
            if response.candidates:
                first_candidate = response.candidates[0]
                if first_candidate.content is not None:
                    contents.append(
                        cast(genai_types.Content, first_candidate.content)  # type: ignore[arg-type]
                    )

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
                    args: dict[str, Any] = raw_args_obj
                else:
                    try:
                        args = dict(raw_args_obj)  # type: ignore[arg-type]
                    except Exception:
                        args = {}

                result = await service.call_tool(name, args)

                function_response_part = genai_types.Part.from_function_response(
                    name=name,
                    response={"result": result},
                )

                contents.append(
                    genai_types.Content(
                        role="tool",
                        parts=[function_response_part],
                    )
                )

            continue

        # no function call
        text = response.text or ""
        if text:
            final_chunks.append(text)
        break

    return "\n".join(final_chunks) if final_chunks else ""
