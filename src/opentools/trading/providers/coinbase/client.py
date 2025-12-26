from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .clients import (
    get_account as _get_account,
)
from .clients import (
    list_accounts as _list_accounts,
)
from .transport import CoinbaseTransport


@dataclass
class CoinbaseClient:
    transport: CoinbaseTransport
    provider: str = "coinbase"

    async def list_accounts(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        retail_portfolio_id: str | None = None,
    ) -> dict[str, Any]:
        return await _list_accounts(
            self.transport,
            limit=limit,
            cursor=cursor,
            retail_portfolio_id=retail_portfolio_id,
        )

    async def get_account(self, account_uuid: str | None = None) -> dict[str, Any]:
        if account_uuid:
            return await _get_account(self.transport, account_uuid)

        data = await _list_accounts(self.transport, limit=1)
        accounts = data.get("accounts") or []
        if not accounts:
            return {}
        return accounts[0]

    # stubs

    async def list_positions(self) -> list[dict[str, Any]]:
        raise NotImplementedError("Positions not implemented for Coinbase yet")

    async def get_position(self, symbol_or_asset_id: str) -> dict[str, Any]:
        raise NotImplementedError("Positions not implemented for Coinbase yet")

    async def get_clock(self) -> dict[str, Any]:
        raise NotImplementedError("Clock not implemented for Coinbase yet")

    async def list_assets(
        self,
        *,
        status: str | None = None,
        asset_class: str | None = None,
        exchange: str | None = None,
        attributes: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError("Assets not implemented for Coinbase yet")

    async def get_asset(self, symbol_or_asset_id: str) -> dict[str, Any]:
        raise NotImplementedError("Assets not implemented for Coinbase yet")

    async def list_orders(
        self,
        *,
        status: str | None = None,
        limit: int | None = None,
        after: str | None = None,
        until: str | None = None,
        direction: str | None = None,
        nested: bool | None = None,
        symbols: list[str] | None = None,
        side: str | None = None,
        asset_class: list[str] | None = None,
        before_order_id: str | None = None,
        after_order_id: str | None = None,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError("Orders not implemented for Coinbase yet")

    async def get_order(
        self,
        order_id: str,
        *,
        nested: bool | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError("Orders not implemented for Coinbase yet")

    async def get_portfolio_history(
        self,
        *,
        period: str | None = None,
        timeframe: str | None = None,
        intraday_reporting: str | None = None,
        start: str | None = None,
        end: str | None = None,
        pnl_reset: str | None = None,
        cashflow_types: str | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError("Portfolio history not implemented for Coinbase yet")
