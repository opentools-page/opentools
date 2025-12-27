from __future__ import annotations

from typing import Any

from .._endpoints import POSITION_PATH, POSITIONS_PATH
from ..transport import AlpacaTransport


async def list_positions(transport: AlpacaTransport) -> list[dict[str, Any]]:
    return await transport.get_list_json(POSITIONS_PATH)


async def get_position(
    transport: AlpacaTransport, symbol_or_asset_id: str
) -> dict[str, Any]:
    path = POSITION_PATH.format(symbol_or_asset_id=symbol_or_asset_id)
    return await transport.get_dict_json(path)
