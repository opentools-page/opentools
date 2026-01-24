from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Any, Awaitable, Callable, cast

from opentools.core.bundles import cached_bundle_for
from opentools.core.errors import ProviderError, ValidationError
from opentools.core.tools import ToolBundle, ToolInput, ToolSpec
from opentools.core.types import FrameworkName, ModelName

from ..schemas import (
    Account,
    Asset,
    Clock,
    Order,
    Portfolio,
    PortfolioBreakdown,
    PortfolioHistory,
    Position,
)
from .provider import TradingProviderClient

if TYPE_CHECKING:
    from .multi import MultiTradingService


@dataclass
class TradingService(Sequence[Any]):
    """
    Canonical trading domain API.
    """

    client: TradingProviderClient
    model: ModelName

    account_mapper: Callable[[dict], Account]
    position_mapper: Callable[[dict], Position | None]
    clock_mapper: Callable[[dict], Clock]
    asset_mapper: Callable[[dict], Asset | None] | None = None
    order_mapper: Callable[[dict], Order | None] | None = None

    portfolio_history_mapper: Callable[[dict], PortfolioHistory] | None = None
    portfolio_mapper: Callable[[dict], Portfolio | None] | None = None
    portfolio_breakdown_mapper: Callable[[dict], PortfolioBreakdown] | None = None

    framework: FrameworkName | None = None

    include: tuple[str, ...] = field(default_factory=tuple)
    exclude: tuple[str, ...] = field(default_factory=tuple)

    # hiding or not hiding specific provider fields
    minimal: bool = False

    # tool error handling policy (LLM adapters can read this)
    fatal_tool_error_kinds: tuple[str, ...] = ("auth", "config")

    _bundle_cache: dict[
        tuple[ModelName, tuple[str, ...], tuple[str, ...]], ToolBundle
    ] = field(default_factory=dict, init=False, repr=False)

    @property
    def provider(self) -> str:
        return getattr(self.client, "provider", "unknown")

    # core api
    async def get_account(self, account_uuid: str | None = None) -> Account:
        raw = await self.client.get_account(account_uuid)
        return self.account_mapper(raw)

    def strict(self) -> "TradingService":
        """
        Raise immediately on fatal tool errors (auth/config by default).
        Best for production.
        """
        return replace(self, fatal_tool_error_kinds=("auth", "config"))

    def demo(self) -> "TradingService":
        """
        Never raise based on tool error kinds.
        Tool failures are returned to the model as ok:false payloads.
        Best for demos / prototyping.
        """
        return replace(self, fatal_tool_error_kinds=())

    async def list_accounts(
        self,
        *,
        limit: int | None = None,
        cursor: str | None = None,
        retail_portfolio_id: str | None = None,
    ) -> list[Account]:
        client_fn = getattr(self.client, "list_accounts", None)
        if client_fn is None or not callable(client_fn):
            raise ProviderError(
                message=f"{self.provider!r} client does not support list_accounts().",
                domain="trading",
                provider=self.provider,
                status_code=None,
            )

        typed_client_fn = cast(Callable[..., Awaitable[Any]], client_fn)

        raw = await typed_client_fn(
            limit=limit,
            cursor=cursor,
            retail_portfolio_id=retail_portfolio_id,
        )

        accounts_raw: list[dict[str, Any]] = []

        if isinstance(raw, dict):
            maybe_accounts = raw.get("accounts")
            if isinstance(maybe_accounts, list):
                accounts_raw = [a for a in maybe_accounts if isinstance(a, dict)]
            else:
                accounts_raw = [raw]
        elif isinstance(raw, list):
            accounts_raw = [a for a in raw if isinstance(a, dict)]
        else:
            raise ProviderError(
                message="Unexpected list_accounts() response shape from provider.",
                domain="trading",
                provider=self.provider,
                status_code=None,
            )

        out: list[Account] = []
        for item in accounts_raw:
            out.append(self.account_mapper(item))
        return out

    # positions
    async def list_positions(
        self,
        *,
        portfolio_type: str | None = None,
        currency: str | None = None,
    ) -> list[Position]:
        client_fn = getattr(self.client, "list_positions", None)
        if client_fn is None or not callable(client_fn):
            raise ProviderError(
                message=f"{self.provider!r} client does not support list_positions().",
                domain="trading",
                provider=self.provider,
                status_code=None,
            )

        typed_client_fn = cast(
            Callable[..., Awaitable[list[dict[str, Any]]]], client_fn
        )

        # Coinbase supports these params; Alpaca doesn't.
        if self.provider == "coinbase":
            raw_list = await typed_client_fn(
                portfolio_type=portfolio_type,
                currency=currency,
            )
        else:
            raw_list = await typed_client_fn()

        out: list[Position] = []
        for item in raw_list:
            p = self.position_mapper(item)
            if p is not None:
                out.append(p)
        return out

    async def get_position(self, symbol_or_asset_id: str) -> Position | None:
        raw = await self.client.get_position(symbol_or_asset_id)
        return self.position_mapper(raw)

    # clock
    async def get_clock(self) -> Clock:
        if self.provider == "coinbase":
            raise ProviderError(
                message=(
                    "get_clock() is not supported for provider 'coinbase'. "
                    "Crypto trades 24/7 and the Coinbase Advanced Trade API "
                    "does not expose a market-hours clock endpoint."
                ),
                domain="trading",
                provider=self.provider,
                status_code=None,
            )

        client_fn = getattr(self.client, "get_clock", None)
        if client_fn is None or not callable(client_fn):
            raise ProviderError(
                message=f"{self.provider!r} client does not support get_clock().",
                domain="trading",
                provider=self.provider,
                status_code=None,
            )

        typed_client_fn = cast(Callable[[], Awaitable[dict[str, Any]]], client_fn)
        raw = await typed_client_fn()
        return self.clock_mapper(raw)

    # assets
    async def list_assets(
        self,
        *,
        status: str | None = None,
        asset_class: str | None = None,
        exchange: str | None = None,
        attributes: list[str] | None = None,
        limit: int | None = 20,
    ) -> list[Asset]:
        if self.asset_mapper is None:
            raise ProviderError(
                message=f"Assets not supported for provider {self.provider!r}",
                domain="trading",
                provider=self.provider,
            )

        raw_list = await self.client.list_assets(
            status=status,
            asset_class=asset_class,
            exchange=exchange,
            attributes=attributes,
        )

        out: list[Asset] = []
        max_items = limit or len(raw_list)
        for item in raw_list:
            a = self.asset_mapper(item)
            if a is not None:
                out.append(a)
            if len(out) >= max_items:
                break
        return out

    async def get_asset(self, symbol_or_asset_id: str) -> Asset | None:
        if self.asset_mapper is None:
            raise ProviderError(
                message=f"Assets not supported for provider {self.provider!r}",
                domain="trading",
                provider=self.provider,
            )

        raw = await self.client.get_asset(symbol_or_asset_id)
        return self.asset_mapper(raw)

    # orders
    async def list_orders(
        self,
        *,
        status: str | None = None,
        limit: int | None = 20,
        after: str | None = None,
        until: str | None = None,
        direction: str | None = None,
        nested: bool | None = None,
        symbols: list[str] | None = None,
        side: str | None = None,
        asset_class: list[str] | None = None,
        before_order_id: str | None = None,
        after_order_id: str | None = None,
    ) -> list[Order]:
        if self.order_mapper is None:
            raise ProviderError(
                message=f"Orders not supported for provider {self.provider!r}",
                domain="trading",
                provider=self.provider,
            )

        client_fn = getattr(self.client, "list_orders", None)
        if client_fn is None or not callable(client_fn):
            raise ProviderError(
                message=f"{self.provider!r} client does not support list_orders().",
                domain="trading",
                provider=self.provider,
            )

        typed_client_fn = cast(
            Callable[..., Awaitable[list[dict[str, Any]]]], client_fn
        )

        raw_list = await typed_client_fn(
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

        out: list[Order] = []
        max_items = limit or len(raw_list)
        for item in raw_list:
            o = self.order_mapper(item)
            if o is not None:
                out.append(o)
            if len(out) >= max_items:
                break
        return out

    async def get_order(
        self,
        order_id: str | None = None,
        *,
        nested: bool | None = None,
    ) -> Order | None:
        if self.order_mapper is None:
            raise ProviderError(
                message=f"Orders not supported for provider {self.provider!r}",
                domain="trading",
                provider=self.provider,
            )

        if not order_id:
            raise ValidationError(
                message="order_id is required for get_order().",
                domain="trading",
                provider=self.provider,
                field_errors=[
                    {
                        "loc": ["order_id"],
                        "msg": "missing",
                        "type": "value_error.missing",
                    }
                ],
            )

        client_fn = getattr(self.client, "get_order", None)
        if client_fn is None or not callable(client_fn):
            raise ProviderError(
                message=f"{self.provider!r} client does not support get_order().",
                domain="trading",
                provider=self.provider,
            )

        typed_client_fn = cast(Callable[..., Awaitable[dict[str, Any]]], client_fn)
        raw = await typed_client_fn(order_id=order_id, nested=nested)
        return self.order_mapper(raw)

    # portfolio breakdown (Coinbase-specific feature)
    async def get_portfolio_breakdown(
        self,
        *,
        portfolio_uuid: str,
        currency: str | None = None,
    ) -> PortfolioBreakdown:
        if self.portfolio_breakdown_mapper is None:
            raise ProviderError(
                message=f"Portfolio breakdown not supported for provider {self.provider!r}",
                domain="trading",
                provider=self.provider,
                status_code=None,
            )

        client_fn = getattr(self.client, "get_portfolio_breakdown", None)
        if client_fn is None or not callable(client_fn):
            raise ProviderError(
                message=f"{self.provider!r} client does not support get_portfolio_breakdown().",
                domain="trading",
                provider=self.provider,
                status_code=None,
            )

        typed = cast(Callable[..., Awaitable[dict[str, Any]]], client_fn)
        raw = await typed(portfolio_uuid=portfolio_uuid, currency=currency)
        return self.portfolio_breakdown_mapper(raw)

    # portfolio history
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
    ) -> PortfolioHistory:
        if self.portfolio_history_mapper is None:
            raise ProviderError(
                message=f"Portfolio history not supported for provider {self.provider!r}",
                domain="trading",
                provider=self.provider,
            )

        raw = await self.client.get_portfolio_history(
            period=period,
            timeframe=timeframe,
            intraday_reporting=intraday_reporting,
            start=start,
            end=end,
            pnl_reset=pnl_reset,
            cashflow_types=cashflow_types,
        )
        return self.portfolio_history_mapper(raw)

    async def list_portfolios(
        self,
        *,
        portfolio_type: str | None = None,
    ) -> list[Portfolio]:
        if self.portfolio_mapper is None:
            raise ProviderError(
                message=f"Portfolios not supported for provider {self.provider!r}",
                domain="trading",
                provider=self.provider,
                status_code=None,
            )

        client_fn = getattr(self.client, "list_portfolios", None)
        if client_fn is None or not callable(client_fn):
            raise ProviderError(
                message=f"{self.provider!r} client does not support list_portfolios().",
                domain="trading",
                provider=self.provider,
                status_code=None,
            )

        typed = cast(Callable[..., Awaitable[Any]], client_fn)
        raw = await typed(portfolio_type=portfolio_type)

        items: list[dict[str, Any]] = []
        if isinstance(raw, list):
            items = [x for x in raw if isinstance(x, dict)]
        elif isinstance(raw, dict):
            maybe = raw.get("portfolios")
            if isinstance(maybe, list):
                items = [x for x in maybe if isinstance(x, dict)]
            else:
                items = [raw]
        else:
            raise ProviderError(
                message="Unexpected list_portfolios() response shape from provider.",
                domain="trading",
                provider=self.provider,
                status_code=None,
            )

        out: list[Portfolio] = []
        for d in items:
            p = self.portfolio_mapper(d)
            if p is not None:
                out.append(p)
        return out

    # tools and bundling
    def tool_specs(
        self,
        *,
        include: Iterable[str] | None = None,
        exclude: Iterable[str] | None = None,
    ) -> list[ToolSpec]:
        effective_include = set(include or self.include)
        effective_exclude = set(exclude or self.exclude)

        ts_self = cast("TradingService", self)

        if self.provider == "alpaca":
            from opentools.trading.providers.alpaca.tools import alpaca_tools

            specs = alpaca_tools(ts_self)
        elif self.provider == "coinbase":
            from opentools.trading.providers.coinbase.tools import coinbase_tools

            specs = coinbase_tools(ts_self)
        else:
            raise ProviderError(
                message=f"Unknown trading provider: {self.provider!r}",
                domain="trading",
                provider=self.provider,
            )

        if effective_include:
            specs = [t for t in specs if t.name in effective_include]
        if effective_exclude:
            specs = [t for t in specs if t.name not in effective_exclude]
        return specs

    def bundle(
        self,
        *,
        include: Iterable[str] | None = None,
        exclude: Iterable[str] | None = None,
        model: ModelName | None = None,
    ) -> ToolBundle:
        resolved = model or self.model

        effective_include = tuple(sorted(set(include or self.include)))
        effective_exclude = tuple(sorted(set(exclude or self.exclude)))

        specs = self.tool_specs(
            include=effective_include,
            exclude=effective_exclude,
        )

        return cached_bundle_for(
            model=resolved,
            specs=specs,
            cache=self._bundle_cache,
            include=effective_include,
            exclude=effective_exclude,
        )

    def framework_tools(self) -> list[Any]:
        from opentools.core.frameworks import framework_tools as _fw_tools

        return _fw_tools(self)

    @property
    def tools(self) -> list[Any]:
        return self.bundle().tools

    async def call_tool(self, tool_name: str, tool_input: ToolInput) -> Any:
        return await self.bundle().call(tool_name, tool_input)

    # sequence, combining
    def _tool_list_for_iteration(self) -> list[Any]:
        if self.framework is not None:
            return self.framework_tools()
        return self.tools

    def __len__(self) -> int:
        return len(self._tool_list_for_iteration())

    def __getitem__(self, index: int | slice) -> Any:
        tools = self._tool_list_for_iteration()
        return tools[index]

    def __iter__(self) -> Iterator[Any]:
        return iter(self._tool_list_for_iteration())

    # adding
    def __add__(self, other: Any) -> MultiTradingService:
        from .multi import MultiTradingService, combine  # runtime import

        if not isinstance(other, (TradingService, MultiTradingService)):
            return NotImplemented  # type: ignore[return-value]

        return combine(self, other)

    def __radd__(self, other: Any) -> MultiTradingService:
        from .multi import MultiTradingService, combine  # runtime import

        if other == 0:
            return combine(self)

        if isinstance(other, (TradingService, MultiTradingService)):
            return combine(other, self)

        return NotImplemented  # type: ignore[return-value]
