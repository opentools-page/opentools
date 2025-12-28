from __future__ import annotations

from typing import Any, Protocol


class TradingProviderClient(Protocol):
    provider: str

    # account
    async def get_account(self, account_uuid: str | None = None) -> dict: ...

    async def list_accounts(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        retail_portfolio_id: str | None = None,
    ) -> dict[str, Any]: ...

    # positions
    async def list_positions(self) -> list[dict]: ...
    async def get_position(self, symbol_or_asset_id: str) -> dict: ...

    # assets
    async def list_assets(
        self,
        *,
        status: str | None = None,
        asset_class: str | None = None,
        exchange: str | None = None,
        attributes: list[str] | None = None,
    ) -> list[dict]: ...

    async def get_asset(self, symbol_or_asset_id: str) -> dict: ...

    # orders
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
    ) -> list[dict]: ...

    async def get_order(
        self,
        order_id: str,
        *,
        nested: bool | None = None,
    ) -> dict: ...

    # portfolio_history
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
    ) -> dict: ...

    # # portfolios (coinbase only)
    # async def list_portfolios(
    #     self,
    #     *,
    #     portfolio_type: str | None = None,
    # ) -> list[dict]: ...

    # # clock
    # async def get_clock(self) -> dict: ...
