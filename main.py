import asyncio
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from opentools import trading
from opentools.adapters.models.openai import run_with_tools


async def main() -> None:
    # load OPENAI_API_KEY, ALPACA_KEY, ALPACA_SECRET from .env
    load_dotenv()

    # this quickstart uses no framework just the model
    client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

    # add the alpaca tools
    service = trading.alpaca(
        api_key=os.environ["ALPACA_KEY"],
        api_secret=os.environ["ALPACA_SECRET"],
        # specify the model, this is required for bundling tools correctly
        model="openai",
        # specify paper trading account or live trading account
        paper=True,
        # specify minimal output returned to model (maximum token efficiency)
        minimal=True,
    )

    prompt = "Show my account summary and list any open positions."

    # run_with_tools creates the tool-loop to make your developement-time quicker
    result = await run_with_tools(
        client=client,
        model="gpt-4.1-mini",
        service=service,
        user_prompt=prompt,
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
