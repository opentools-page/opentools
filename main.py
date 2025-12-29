from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv
from pydantic_ai import Agent

from opentools import trading

load_dotenv()


async def main() -> None:
    tools = trading.alpaca(
        api_key=os.environ["ALPACA_KEY"],
        api_secret=os.environ["ALPACA_SECRET"],
        model="gemini",
        framework="pydantic_ai",
        paper=True,
    )

    agent = Agent(
        "google-gla:gemini-2.5-flash",
        tools=tools,
        system_prompt=(
            "You are a trading assistant with access to Alpaca tools. "
            "Prefer calling tools when asked about account, positions, "
            "assets, or orders."
        ),
    )

    user_prompt = (
        "get my account -- return solely the pydantic object in json you receive"
    )

    result = await agent.run(user_prompt)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
