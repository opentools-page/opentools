from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .clients import get_account as _get_account
from .clients import list_accounts as _list_accounts
from .clients.assets import get_asset as _get_asset
from .clients.assets import list_assets as _list_assets
from .clients.orders import get_order as _get_order
from .clients.orders import list_orders as _list_orders
from .clients.portfolio import (
    get_portfolio_breakdown as _get_portfolio_breakdown,
)
from .clients.portfolio import (
    list_portfolios as _list_portfolios,
)
from .transport import CoinbaseTransport


@dataclass
class CoinbaseClient:
    transport: CoinbaseTransport
    provider: str = "coinbase"

    # ---------- accounts ----------

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
            data = await _get_account(self.transport, account_uuid)
            account = data.get("account") or data
            return account

        data = await _list_accounts(self.transport, limit=1)
        accounts = data.get("accounts") or []
        if not accounts:
            return {}

        primary = dict(accounts[0])
        primary["_opentools_primary_fallback"] = True
        return primary

    # ---------- portfolios ----------

    async def list_portfolios(
        self,
        *,
        portfolio_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Wraps GET /api/v3/brokerage/portfolios and returns the list under 'portfolios'.
        """
        data = await _list_portfolios(
            self.transport,
            portfolio_type=portfolio_type,
        )
        portfolios = data.get("portfolios") or []
        # defensive: ensure we always return a list[dict[str, Any]]
        if not isinstance(portfolios, list):
            return []
        return portfolios

    # ---------- positions (derived from portfolio breakdown) ----------

    async def list_positions(
        self,
        *,
        portfolio_type: str | None = None,
        currency: str | None = None,
    ) -> list[dict[str, Any]]:
        portfolios: list[dict[str, Any]] = []

        if portfolio_type:
            resp = await _list_portfolios(
                self.transport,
                portfolio_type=portfolio_type,
            )
            portfolios = resp.get("portfolios") or []
        else:
            # default
            for pt in ("DEFAULT", "UNDEFINED"):
                resp = await _list_portfolios(
                    self.transport,
                    portfolio_type=pt,
                )
                portfolios = resp.get("portfolios") or []
                if portfolios:
                    break

        if not isinstance(portfolios, list) or not portfolios:
            return []

        portfolio_uuid = portfolios[0].get("uuid")
        if not portfolio_uuid:
            return []

        breakdown = await _get_portfolio_breakdown(
            self.transport,
            portfolio_uuid=portfolio_uuid,
            currency=currency,
        )

        if not isinstance(breakdown, dict):
            return []

        positions: list[dict[str, Any]] = []

        # spot positions
        for item in breakdown.get("spot_positions") or []:
            row = dict(item)
            row["_opentools_position_kind"] = "spot"
            positions.append(row)

        # perpetual futures positions
        for item in breakdown.get("perp_positions") or []:
            row = dict(item)
            row["_opentools_position_kind"] = "perp"
            positions.append(row)

        # dated futures positions
        for item in breakdown.get("futures_positions") or []:
            row = dict(item)
            row["_opentools_position_kind"] = "future"
            positions.append(row)

        return positions

    async def get_position(self, symbol_or_asset_id: str) -> dict[str, Any]:
        """
        Not wired yet. Could be implemented later by:
        - calling list_positions(), then
        - filtering by symbol/product_id.
        """
        raise NotImplementedError("get_position is not implemented for Coinbase yet")

    # ---------- orders ----------

    async def list_orders(
        self,
        *,
        status: str | None = None,
        limit: int | None = None,
        after: str | None = None,
        until: str | None = None,
        direction: str | None = None,  # unused
        nested: bool | None = None,  # unused
        symbols: list[str] | None = None,
        side: str | None = None,
        asset_class: list[str] | None = None,  # unused
        before_order_id: str | None = None,  # unused
        after_order_id: str | None = None,  # unused
    ) -> list[dict[str, Any]]:
        data = await _list_orders(
            self.transport,
            limit=limit,
            cursor=None,
            product_ids=symbols,
            order_status=status,
            order_side=side,
            start_date=after,
            end_date=until,
        )
        orders = data.get("orders") or []
        return orders

    async def get_order(
        self,
        order_id: str,
        *,
        nested: bool | None = None,
    ) -> dict[str, Any]:
        data = await _get_order(self.transport, order_id)
        order = data.get("order") if isinstance(data, dict) else None
        return order or data

    # ---------- assets / products ----------

    async def list_assets(
        self,
        *,
        status: str | None = None,
        asset_class: str | None = None,
        exchange: str | None = None,
        attributes: list[str] | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> list[dict[str, Any]]:
        return await _list_assets(
            self.transport,
            status=status,
            asset_class=asset_class,
            exchange=exchange,
            attributes=attributes,
            limit=limit,
            cursor=cursor,
        )

    async def get_asset(self, symbol_or_asset_id: str) -> dict[str, Any]:
        data = await _get_asset(self.transport, product_id=symbol_or_asset_id)
        return data

    # ---------- unsupported / stubs ----------

    async def get_clock(self) -> dict[str, Any]:
        raise NotImplementedError("Clock not implemented for Coinbase yet")

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
