from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class FinanceProviderClient(Protocol):
    provider: str

    async def get_account(self) -> dict: ...
    async def list_positions(self) -> list[dict]: ...

    # Optional for later:
    async def get_quote(self, symbol: str) -> dict: ...
    async def place_order(self, payload: dict) -> dict: ...


@dataclass
class FinanceService:
    client: FinanceProviderClient

    async def get_account(self) -> dict:
        return await self.client.get_account()

    async def list_positions(self) -> list[dict]:
        return await self.client.list_positions()
