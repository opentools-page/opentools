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
        minimal=True,
    )

    agent = Agent(
        "google-gla:gemini-2.5-flash",
        tools=tools,
        system_prompt=(
            """You are a trading assistant that has access to coinbase tools. Be sure to provide
            when required"""
        ),
    )

    user_prompt = "list 5 diferent assets on coinbase for me please - give me raw ouptput you receive"

    result = await agent.run(user_prompt)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
