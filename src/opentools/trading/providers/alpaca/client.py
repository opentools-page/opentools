from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .clients import get_account, get_clock, list_positions
from .transport import AlpacaTransport


@dataclass
class AlpacaClient:
    """
    Thin wrapper over the Alpaca HTTP clients.
    """

    transport: AlpacaTransport
    provider: str = "alpaca"

    async def get_account(self) -> dict[str, Any]:
        """Return raw Alpaca account JSON."""
        return await get_account(self.transport)

    async def list_positions(self) -> list[dict[str, Any]]:
        """Return raw Alpaca positions JSON (list of objects)."""
        return await list_positions(self.transport)

    async def get_clock(self) -> dict[str, Any]:
        """Return raw Alpaca trading clock JSON."""
        return await get_clock(self.transport)
