from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from opentools import trading
from opentools.adapters.models.openai import run_with_tools

load_dotenv()


async def main() -> None:
    tools = trading.coinbase(
        api_key=os.environ["COINBASE_KEY"],
        api_secret=os.environ["COINBASE_SECRET"],
        model="openai",
        paper=False,
        minimal=True,
    )

    client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

    prompt = (
        "Get my portfolios. Pick one example portfolio ID and check positions. "
        "If there are no positions, say so."
    )

    text = await run_with_tools(
        client=client,
        model="gpt-4.1-mini",
        service=tools,
        user_prompt=prompt,
        max_rounds=8,
        max_tokens=600,
    )

    print(text)


if __name__ == "__main__":
    asyncio.run(main())
