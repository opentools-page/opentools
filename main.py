import asyncio

from opentools.finance import alpaca


async def main():
    svc = alpaca(key_id="...", secret_key="...", paper=True)
    print(await svc.get_account())
    print(await svc.list_positions())


asyncio.run(main())
