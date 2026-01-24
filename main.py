from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from dotenv import load_dotenv

from opentools import trading
from opentools.adapters.frameworks.pydantic_ai import tools_for_service

load_dotenv()


def _dump(x: Any) -> str:
    return json.dumps(x, indent=2, default=str)


def _pick_tool(tools: list[Any], prefer: str) -> Any:
    prefer = prefer.lower()
    for t in tools:
        name = getattr(t, "name", "") or ""
        if prefer in name.lower():
            return t
    return tools[0]


async def _call_pydantic_tool(tool: Any, args: dict[str, Any]) -> Any:
    fn = getattr(tool, "function", None) or getattr(tool, "func", None)
    if fn is None:
        raise RuntimeError(
            f"Pydantic Tool {getattr(tool, 'name', '<unknown>')} has no callable function"
        )

    if asyncio.iscoroutinefunction(fn):
        return await fn(**args)

    out = fn(**args)
    if asyncio.iscoroutine(out):
        return await out
    return out


async def test_pydantic_adapter_strict() -> None:
    print(
        "\n=== A) PydanticAI adapter path + BAD auth (STRICT service: should RAISE) ==="
    )

    service = trading.coinbase(
        api_key=os.environ["COINBASE_KEY"],
        api_secret="yooooo",
        model="openai",
        paper=False,
        minimal=True,
    ).strict()

    tools = tools_for_service(service)
    tool = _pick_tool(tools, prefer="portfolio")

    print(f"Using tool: {tool.name!r}")

    try:
        _ = await _call_pydantic_tool(tool, {})
        print("UNEXPECTED: no exception raised")
    except Exception as e:
        print("Raised as expected:")
        print(type(e).__name__, str(e))


async def test_pydantic_adapter_demo() -> None:
    print(
        "\n=== B) PydanticAI adapter path + BAD auth (DEMO service: should NOT raise) ==="
    )

    service = trading.coinbase(
        api_key=os.environ["COINBASE_KEY"],
        api_secret="yooooo",
        model="openai",
        paper=False,
        minimal=True,
    ).demo()

    tools = tools_for_service(service)
    tool = _pick_tool(tools, prefer="portfolio")

    print(f"Using tool: {tool.name!r}")

    result = await _call_pydantic_tool(tool, {})
    print(_dump(result))


async def test_pydantic_adapter_fatal_override() -> None:
    print("\n=== C) PydanticAI adapter path + override fatal_kinds ===")

    service = trading.coinbase(
        api_key=os.environ["COINBASE_KEY"],
        api_secret="yooooo",
        model="openai",
        paper=False,
        minimal=True,
    ).demo()

    tools = tools_for_service(service, fatal_kinds=("auth", "config"))
    tool = _pick_tool(tools, prefer="portfolio")

    print(f"Using tool: {tool.name!r}")

    try:
        _ = await _call_pydantic_tool(tool, {})
        print("UNEXPECTED: no exception raised")
    except Exception as e:
        print("Raised as expected (override forced fatal):")
        print(type(e).__name__, str(e))


async def test_direct_unknown_tool_call() -> None:
    print("\n=== D) Direct bundle call: unknown tool (ok:false validation) ===")

    tools = trading.alpaca(
        api_key=os.environ.get("ALPACA_KEY"),
        api_secret=os.environ.get("ALPACA_SECRET"),
        model="openai",
        paper=True,
        minimal=True,
    )

    bundle = tools.bundle()
    result = await bundle.call("definitely_not_a_tool", {})
    print(_dump(result))


async def test_direct_crash() -> None:
    print("\n=== E) Direct tool call: unexpected TypeError (should CRASH) ===")

    tools = trading.alpaca(
        api_key=os.environ.get("ALPACA_KEY"),
        api_secret=os.environ.get("ALPACA_SECRET"),
        model="openai",
        paper=True,
        minimal=True,
    )

    bundle = tools.bundle()
    safe_tool_name = next(iter(bundle.dispatch.keys()))
    spec = bundle.dispatch[safe_tool_name]
    print(f"Using tool: safe={safe_tool_name!r} canonical={spec.name!r}")

    await bundle.call(safe_tool_name, {"definitely_not_a_param": "lol"})


async def main() -> None:
    await test_pydantic_adapter_strict()
    await test_pydantic_adapter_demo()
    await test_pydantic_adapter_fatal_override()
    await test_direct_unknown_tool_call()

    if os.environ.get("RUN_CRASH_TEST") == "1":
        await test_direct_crash()
    else:
        print("\n(skip) E) crash test disabled (set RUN_CRASH_TEST=1 to enable)")


if __name__ == "__main__":
    asyncio.run(main())
