from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .clients import (
    get_account,
    get_clock,
    get_position,
    list_positions,
)
from .clients.assets import get_asset as _get_asset
from .clients.assets import list_assets as _list_assets
from .clients.orders import get_order as _get_order
from .clients.orders import list_orders as _list_orders
from .clients.portfolio import (
    get_portfolio_history as _get_portfolio_history,
)
from .transport import AlpacaTransport


@dataclass
class AlpacaClient:
    """
    Thin wrapper around Alpaca HTTP client functions.
    """

    transport: AlpacaTransport
    provider: str = "alpaca"

    async def get_account(self) -> dict[str, Any]:
        return await get_account(self.transport)

    async def list_positions(self) -> list[dict[str, Any]]:
        return await list_positions(self.transport)

    async def get_position(self, symbol_or_asset_id: str) -> dict[str, Any]:
        return await get_position(self.transport, symbol_or_asset_id)

    async def get_clock(self) -> dict[str, Any]:
        return await get_clock(self.transport)

    async def list_assets(
        self,
        *,
        status: str | None = None,
        asset_class: str | None = None,
        exchange: str | None = None,
        attributes: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        return await _list_assets(
            self.transport,
            status=status,
            asset_class=asset_class,
            exchange=exchange,
            attributes=attributes,
        )

    async def get_asset(self, symbol_or_asset_id: str) -> dict[str, Any]:
        return await _get_asset(self.transport, symbol_or_asset_id)

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
        return await _list_orders(
            self.transport,
            status=status,
            limit=limit,
            after=after,
            until=until,
            direction=direction,
            nested=nested,
            symbols=symbols,
            side=side,
            asset_class=asset_class,
            before_order_id=before_order_id,
            after_order_id=after_order_id,
        )

    async def get_order(
        self,
        order_id: str,
        *,
        nested: bool | None = None,
    ) -> dict[str, Any]:
        return await _get_order(self.transport, order_id=order_id, nested=nested)

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
        return await _get_portfolio_history(
            self.transport,
            period=period,
            timeframe=timeframe,
            intraday_reporting=intraday_reporting,
            start=start,
            end=end,
            pnl_reset=pnl_reset,
            cashflow_types=cashflow_types,
        )
