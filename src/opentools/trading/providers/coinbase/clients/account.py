from __future__ import annotations

from typing import Any

from .._endpoints import ACCOUNT_PATH, ACCOUNTS_PATH
from ..transport import CoinbaseTransport


async def list_accounts(
    transport: CoinbaseTransport,
    *,
    limit: int | None = None,
    cursor: str | None = None,
    retail_portfolio_id: str | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if limit is not None:
        params["limit"] = limit
    if cursor is not None:
        params["cursor"] = cursor
    if retail_portfolio_id is not None:
        params["retail_portfolio_id"] = retail_portfolio_id

    return await transport.get_dict_json(ACCOUNTS_PATH, params=params)


async def get_account(
    transport: CoinbaseTransport,
    account_uuid: str,
) -> dict[str, Any]:
    path = ACCOUNT_PATH.format(account_uuid=account_uuid)
    return await transport.get_dict_json(path)
