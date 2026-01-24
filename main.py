from __future__ import annotations

import asyncio
import os
from typing import Any, Awaitable, Callable, Protocol

from dotenv import load_dotenv

from opentools import trading

load_dotenv()


# ----------------------------
# Provider config (env-driven)
# ----------------------------

OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4.1-mini")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-3-7-sonnet-latest")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b-instruct")


USER_PROMPT = "Get my portfolios."
MAX_ROUNDS = 3


# ----------------------------
# Minimal typing glue
# ----------------------------


class Runner(Protocol):
    async def __call__(
        self,
        *,
        client: Any,
        model: str,
        service: Any,
        user_prompt: str,
        max_rounds: int,
    ) -> str: ...


def _require_env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        raise RuntimeError(f"Missing required env var: {name}")
    return v


# ----------------------------
# Provider-specific clients + runners
# ----------------------------


def _ollama_client():
    from ollama import AsyncClient

    return AsyncClient(host=OLLAMA_HOST)


async def _ollama_run(
    *, client: Any, model: str, service: Any, user_prompt: str, max_rounds: int
) -> str:
    from opentools.adapters.models.ollama.chat import run_with_tools

    return await run_with_tools(
        client=client,
        model=model,
        service=service,
        user_prompt=user_prompt,
        max_rounds=max_rounds,
    )


def _openai_client():
    from openai import AsyncOpenAI

    return AsyncOpenAI(api_key=_require_env("OPENAI_API_KEY"))


async def _openai_run(
    *, client: Any, model: str, service: Any, user_prompt: str, max_rounds: int
) -> str:
    from opentools.adapters.models.openai.chat import run_with_tools

    return await run_with_tools(
        client=client,
        model=model,
        service=service,
        user_prompt=user_prompt,
        max_rounds=max_rounds,
    )


def _openrouter_client():
    from openai import AsyncOpenAI

    return AsyncOpenAI(
        api_key=_require_env("OPENROUTER_API_KEY"),
        base_url=os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    )


async def _openrouter_run(
    *, client: Any, model: str, service: Any, user_prompt: str, max_rounds: int
) -> str:
    from opentools.adapters.models.openrouter.chat import run_with_tools

    return await run_with_tools(
        client=client,
        model=model,
        service=service,
        user_prompt=user_prompt,
        max_rounds=max_rounds,
    )


def _anthropic_client():
    from anthropic import AsyncAnthropic

    return AsyncAnthropic(api_key=_require_env("ANTHROPIC_API_KEY"))


async def _anthropic_run(
    *, client: Any, model: str, service: Any, user_prompt: str, max_rounds: int
) -> str:
    from opentools.adapters.models.anthropic.chat import run_with_tools

    return await run_with_tools(
        client=client,
        model=model,
        service=service,
        user_prompt=user_prompt,
        max_rounds=max_rounds,
    )


def _gemini_client():
    import google.genai as genai

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    return genai.Client()


async def _gemini_run(
    *, client: Any, model: str, service: Any, user_prompt: str, max_rounds: int
) -> str:
    from opentools.adapters.models.gemini.chat import run_with_tools

    return await run_with_tools(
        client=client,
        model=model,
        service=service,
        user_prompt=user_prompt,
        max_rounds=max_rounds,
    )


# ----------------------------
# Test harness (STRICT vs DEMO)
# ----------------------------


async def _test_provider(
    *,
    title: str,
    client: Any,
    runner: Runner,
    model: str,
    service_model_tag: str,
) -> None:
    print(f"\n=== {title} (STRICT service: should RAISE) ===")

    strict_service = trading.coinbase(
        api_key=_require_env("COINBASE_KEY"),
        api_secret="yooooo",  # wrong on purpose
        model=service_model_tag,
        paper=False,
        minimal=True,
    ).strict()

    try:
        _ = await runner(
            client=client,
            model=model,
            service=strict_service,
            user_prompt=USER_PROMPT,
            max_rounds=MAX_ROUNDS,
        )
        print("UNEXPECTED: no exception raised")
    except Exception as e:
        print("Raised as expected:")
        print(type(e).__name__, str(e))

    print(
        f"\n=== {title} (DEMO service: should NOT raise, should narrate/return ok:false) ==="
    )

    demo_service = trading.coinbase(
        api_key=_require_env("COINBASE_KEY"),
        api_secret="yooooo",  # wrong on purpose
        model=service_model_tag,
        paper=False,
        minimal=True,
    ).demo()

    try:
        text = await runner(
            client=client,
            model=model,
            service=demo_service,
            user_prompt=USER_PROMPT,
            max_rounds=MAX_ROUNDS,
        )
        print(text)
    except Exception as e:
        # If this raises, something’s wrong with your “demo shouldn’t raise” expectation
        print("UNEXPECTED: demo run raised:")
        print(type(e).__name__, str(e))


async def main() -> None:
    # Ollama
    await _test_provider(
        title="Ollama",
        client=_ollama_client(),
        runner=_ollama_run,
        model=OLLAMA_MODEL,
        service_model_tag="ollama",
    )

    # OpenAI
    await _test_provider(
        title="OpenAI",
        client=_openai_client(),
        runner=_openai_run,
        model=OPENAI_MODEL,
        service_model_tag="openai",
    )

    # OpenRouter
    await _test_provider(
        title="OpenRouter",
        client=_openrouter_client(),
        runner=_openrouter_run,
        model=OPENROUTER_MODEL,
        service_model_tag="openrouter",
    )

    # Anthropic
    await _test_provider(
        title="Anthropic",
        client=_anthropic_client(),
        runner=_anthropic_run,
        model=ANTHROPIC_MODEL,
        service_model_tag="anthropic",
    )

    # Gemini
    await _test_provider(
        title="Gemini",
        client=_gemini_client(),
        runner=_gemini_run,
        model=GEMINI_MODEL,
        service_model_tag="gemini",
    )


if __name__ == "__main__":
    asyncio.run(main())
