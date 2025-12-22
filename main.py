import asyncio
import os

from anthropic import AsyncAnthropic
from dotenv import load_dotenv

from opentools import trading
from opentools.adapters.anthropic.chat import run_with_tools

load_dotenv()


async def main() -> None:
    client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    svc = trading.alpaca(
        key_id=os.environ["ALPACA_KEY"],
        secret_key=os.environ["ALPACA_SECRET"],
        paper=True,
        model="anthropic",
    )

    answer = await run_with_tools(
        client=client,
        model="claude-3-5-haiku-20241022",
        service=svc,
        user_prompt=(
            "You MUST call clock related function before summarizing. "
            "Then give me a human-friendly summary."
        ),
    )

    print(answer)


if __name__ == "__main__":
    asyncio.run(main())
