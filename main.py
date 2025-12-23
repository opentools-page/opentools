# main_openrouter.py
from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from opentools import trading
from opentools.adapters.models.openrouter.chat import run_with_tools

load_dotenv()


async def main() -> None:
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )

    svc = trading.alpaca(
        key_id=os.environ["ALPACA_KEY"],
        secret_key=os.environ["ALPACA_SECRET"],
        model="openrouter",
    )

    answer = await run_with_tools(
        client=client,
        model="openai/gpt-4o-mini",
        service=svc,
        user_prompt="List the Alpaca trading tools you have available, just their names.",
        max_rounds=3,
        max_tokens=400,
    )

    print(answer)


if __name__ == "__main__":
    asyncio.run(main())
