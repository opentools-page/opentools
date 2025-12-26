from __future__ import annotations

from typing import Any

from .._endpoints import CLOCK_PATH
from ..transport import AlpacaTransport


async def get_clock(transport: AlpacaTransport) -> dict[str, Any]:
    return await transport.get_dict_json(CLOCK_PATH)
