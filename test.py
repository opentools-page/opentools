from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv

from opentools import trading

load_dotenv()


async def main() -> None:
    service = trading.coinbase(
        api_key=os.environ["COINBASE_KEY"],
        api_secret=os.environ["COINBASE_SECRET"],
        model="gemini",
        framework=None,  # no Pydantic-AI; call service directly
        paper=False,
    )

    # 1) Single account (canonical)
    account = await service.get_account()
    print("get_account type:", type(account))
    print("get_account:", account.model_dump())

    # 2) List accounts (canonical list)
    accounts = await service.list_accounts(limit=5)
    print("list_accounts type:", type(accounts))
    for i, acc in enumerate(accounts):
        print(f"  [{i}] {type(acc)} ->", acc.model_dump())

    # 3) Positions (will be [] until you wire position_from_coinbase)
    positions = await service.list_positions()
    print("list_positions:", positions)


asyncio.run(main())
