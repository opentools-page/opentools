from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv
from langchain.agents import create_agent as create_react_agent
from langchain_openai import ChatOpenAI

from opentools import trading

load_dotenv()


async def main() -> None:
    svc = trading.coinbase(
        api_key=os.environ["COINBASE_KEY"],
        api_secret=os.environ["COINBASE_SECRET"],
        model="openai",
        framework="langgraph",
    )

    llm = ChatOpenAI(model="gpt-4.1-mini")

    agent = create_react_agent(
        llm,
        tools=svc,
        system_prompt=(
            "You are a trading assistant. "
            "Use the provided tools to inspect the user's Coinbase account. "
            "First, list the tools you have, then call one or two that are useful."
        ),
    )

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Break down coinbase information."}]}
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
