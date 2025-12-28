from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv
from pydantic_ai import Agent

from opentools import trading

load_dotenv()


async def main() -> None:
    tools = trading.coinbase(
        api_key=os.environ["COINBASE_KEY"],
        api_secret=os.environ["COINBASE_SECRET"],
        model="gemini",
        framework="pydantic_ai",
        paper=False,
    )

    agent = Agent(
        "google-gla:gemini-2.5-flash",
        tools=tools,
        system_prompt=(
            "You are a trading assistant with access to Coinbase tools. "
            "Prefer calling tools when asked about account, positions, "
            "assets, or orders."
        ),
    )

    user_prompt = (
        "list all tools and then obtain all my portfolios with coinbase please"
    )

    result = await agent.run(user_prompt)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
