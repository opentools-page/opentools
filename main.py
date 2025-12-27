from __future__ import annotations

import asyncio
import os
from typing import Any, Dict

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel

from opentools import trading

load_dotenv()


class AccountsResult(BaseModel):
    alpaca_account: Dict[str, Any]
    coinbase_accounts_raw: Dict[str, Any]


async def main() -> None:
    alpaca_svc = trading.alpaca(
        api_key=os.environ["ALPACA_KEY"],
        api_secret=os.environ["ALPACA_SECRET"],
        model="openai",
        framework="pydantic_ai",
    )

    coinbase_svc = trading.coinbase(
        api_key=os.environ["COINBASE_KEY"],
        api_secret=os.environ["COINBASE_SECRET"],
        model="openai",
        framework="pydantic_ai",
    )

    tools = alpaca_svc + coinbase_svc

    model = OpenAIChatModel(model_name="gpt-4o-mini")

    agent: Agent[None, AccountsResult] = Agent(
        model=model,
        tools=tools,
        output_type=AccountsResult,
        retries=2,
        output_retries=2,
        system_prompt=(
            "You are a trading assistant.\n"
            "Always use tools instead of guessing account data.\n"
            "You MUST call both `alpaca_get_account` and `coinbase_list_accounts` "
            "before returning a result.\n"
            "In the final answer, return ONLY a JSON object that can be parsed "
            "as AccountsResult (alpaca_account, coinbase_accounts_raw)."
        ),
    )

    user_prompt = """
    1. Call `alpaca_get_account` to fetch my Alpaca account information.
       Use its output as the value for "alpaca_account".

    2. Call `coinbase_list_accounts` to list all my Coinbase accounts.
       Use its raw output as the value for "coinbase_accounts_raw".

    3. Return a single JSON object with those two keys only.
    """

    async with agent:
        result = await agent.run(user_prompt)

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
