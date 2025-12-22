from __future__ import annotations

from typing import Any

from .._endpoints import POSITIONS_PATH
from ..transport import AlpacaTransport


async def list_positions(transport: AlpacaTransport) -> list[dict[str, Any]]:
    return await transport.get_list_json(POSITIONS_PATH)
