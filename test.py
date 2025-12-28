from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv

from opentools import trading
from opentools.trading.schemas import (  # optional imports
    Account,
    Asset,
    Order,
    Position,
)


async def main() -> None:
    load_dotenv()

    service = trading.coinbase(
        api_key=os.environ["COINBASE_KEY"],
        api_secret=os.environ["COINBASE_SECRET"],
        model="gemini",
        framework=None,  # no framework: we call the service directly
        paper=False,
    )

    # ---------- get_account ----------
    print("=== get_account ===")
    acc = await service.get_account()
    print("type:", type(acc))
    print(acc.model_dump())

    # ---------- list_accounts ----------
    print("\n=== list_accounts ===")
    accounts = await service.list_accounts(limit=10)
    print("type:", type(accounts), "len:", len(accounts))
    for i, a in enumerate(accounts):
        print(f"[{i}] {type(a)} -> {a.model_dump()}")

    # ---------- list_portfolios (raw, not yet canonical) ----------
    print("\n=== list_portfolios (raw) ===")
    portfolios = await service.list_portfolios()
    print("type:", type(portfolios), "len:", len(portfolios))
    for i, p in enumerate(portfolios):
        print(f"[{i}] {type(p)} -> {p}")

    # ---------- list_assets ----------
    print("\n=== list_assets (canonical Asset models, truncated) ===")
    assets = await service.list_assets(limit=5, asset_class="crypto")
    print("type:", type(assets), "len:", len(assets))
    for i, asset in enumerate(assets):
        print(f"[{i}] {type(asset)} -> {asset.model_dump()}")

    # ---------- get_asset ----------
    print("\n=== get_asset('BTC-USD') ===")
    try:
        btc = await service.get_asset("BTC-USD")
        print("type:", type(btc))
        print(btc.model_dump() if btc is not None else btc)
    except Exception as e:
        print("get_asset error:", repr(e))

    # ---------- list_orders ----------
    print("\n=== list_orders ===")
    orders = await service.list_orders(limit=10)
    print("type:", type(orders), "len:", len(orders))
    for i, order in enumerate(orders):
        print(f"[{i}] {type(order)} -> {order.model_dump()}")

    # ---------- get_order (if any exist) ----------
    if orders:
        first_id = orders[0].id
        print("\n=== get_order(order_id=first_id) ===")
        order = await service.get_order(order_id=first_id)
        print("type:", type(order))
        print(order.model_dump() if order is not None else order)
    else:
        print("\n=== get_order skipped (no orders) ===")

    # ---------- list_positions (canonical Position models, once mapper is wired) ----------
    print(
        "\n=== list_positions (canonical Positions; expect [] until mapper implemented) ==="
    )
    positions = await service.list_positions()
    print("type:", type(positions), "len:", len(positions))
    for i, pos in enumerate(positions):
        print(f"[{i}] {type(pos)} -> {pos.model_dump()}")


if __name__ == "__main__":
    asyncio.run(main())
