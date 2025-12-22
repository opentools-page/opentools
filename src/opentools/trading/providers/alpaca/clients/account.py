from __future__ import annotations

from typing import Any

from .._endpoints import ACCOUNT_PATH
from ..transport import AlpacaTransport


async def get_account(transport: AlpacaTransport) -> dict[str, Any]:
    return await transport.get_dict_json(ACCOUNT_PATH)
