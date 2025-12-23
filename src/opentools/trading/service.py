from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Iterator, Literal, Protocol

from opentools.core.tools import ToolBundle, ToolInput, ToolSpec

from .schemas import Account, Asset, Clock, Order, Position

ModelName = Literal["anthropic", "openai", "gemini", "ollama", "openrouter"]


class TradingProviderClient(Protocol):
    provider: str

    async def get_account(self) -> dict: ...
    async def list_positions(self) -> list[dict]: ...
    async def get_position(self, symbol_or_asset_id: str) -> dict: ...
    async def get_clock(self) -> dict: ...

    async def list_assets(
        self,
        *,
        status: str | None = None,
        asset_class: str | None = None,
        exchange: str | None = None,
        attributes: list[str] | None = None,
    ) -> list[dict]: ...

    async def get_asset(self, symbol_or_asset_id: str) -> dict: ...

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


@dataclass
class TradingService(Iterable[Any]):
    """
    Neutral trading domain service + tool surface.

    Core:
      - get_account()                  -> Account
      - list_positions()               -> list[Position]
      - get_position(symbol_or_id)     -> Position | None
      - get_clock()                    -> Clock
      - list_assets(...)               -> list[Asset]
      - get_asset(symbol_or_id)        -> Asset | None
      - list_orders(...)               -> list[Order]
      - get_order(order_id, ...)       -> Order | None
    """

    # required
    client: TradingProviderClient
    account_mapper: Callable[[dict], Account]
    position_mapper: Callable[[dict], Position | None]
    clock_mapper: Callable[[dict], Clock]
    model: ModelName

    # optional mappers
    asset_mapper: Callable[[dict], Asset | None] | None = None
    order_mapper: Callable[[dict], Order | None] | None = None

    # service-level tool filters
    include: tuple[str, ...] = field(default_factory=tuple)
    exclude: tuple[str, ...] = field(default_factory=tuple)

    _bundle_cache: dict[
        tuple[ModelName, tuple[str, ...], tuple[str, ...]], ToolBundle
    ] = field(default_factory=dict, init=False, repr=False)

    @property
    def provider(self) -> str:
        return getattr(self.client, "provider", "unknown")

    # ---- core domain ----

    async def get_account(self) -> Account:
        raw = await self.client.get_account()
        return self.account_mapper(raw)

    async def list_positions(self) -> list[Position]:
        raw_list = await self.client.list_positions()
        out: list[Position] = []
        for item in raw_list:
            p = self.position_mapper(item)
            if p is not None:
                out.append(p)
        return out

    async def get_position(self, symbol_or_asset_id: str) -> Position | None:
        raw = await self.client.get_position(symbol_or_asset_id)
        return self.position_mapper(raw)

    async def get_clock(self) -> Clock:
        raw = await self.client.get_clock()
        return self.clock_mapper(raw)

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
            raise NotImplementedError(
                f"Assets not supported for provider {self.provider!r}"
            )

        raw_list = await self.client.list_assets(
            status=status,
            asset_class=asset_class,
            exchange=exchange,
            attributes=attributes,
        )

        out: list[Asset] = []
        for item in raw_list:
            a = self.asset_mapper(item)
            if a is not None:
                out.append(a)
            if limit is not None and len(out) >= limit:
                break
        return out

    async def get_asset(self, symbol_or_asset_id: str) -> Asset | None:
        if self.asset_mapper is None:
            raise NotImplementedError(
                f"Assets not supported for provider {self.provider!r}"
            )
        raw = await self.client.get_asset(symbol_or_asset_id)
        return self.asset_mapper(raw)

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
            raise NotImplementedError(
                f"Orders not supported for provider {self.provider!r}"
            )

        raw_list = await self.client.list_orders(
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
        order_id: str,
        *,
        nested: bool | None = None,
    ) -> Order | None:
        if self.order_mapper is None:
            raise NotImplementedError(
                f"Orders not supported for provider {self.provider!r}"
            )
        raw = await self.client.get_order(order_id, nested=nested)
        return self.order_mapper(raw)

    # ---- tool specs & bundling ----

    def tool_specs(
        self,
        *,
        include: Iterable[str] | None = None,
        exclude: Iterable[str] | None = None,
    ) -> list[ToolSpec]:
        effective_include = set(include or self.include)
        effective_exclude = set(exclude or self.exclude)

        if self.provider == "alpaca":
            from opentools.trading.providers.alpaca.tools import alpaca_tools

            specs = alpaca_tools(self)
        else:
            raise ValueError(f"Unknown trading provider: {self.provider}")

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
        resolved: ModelName = model or self.model

        effective_include = tuple(sorted(set(include or self.include)))
        effective_exclude = tuple(sorted(set(exclude or self.exclude)))

        key = (resolved, effective_include, effective_exclude)
        if key in self._bundle_cache:
            return self._bundle_cache[key]

        specs = self.tool_specs(
            include=effective_include,
            exclude=effective_exclude,
        )

        if resolved == "anthropic":
            from opentools.adapters.models.anthropic.bundle import to_anthropic_bundle

            bundle = to_anthropic_bundle(list(specs))
        elif resolved == "openai":
            from opentools.adapters.models.openai.bundle import to_openai_bundle

            bundle = to_openai_bundle(specs)
        elif resolved == "gemini":
            from opentools.adapters.models.gemini.bundle import to_gemini_bundle

            bundle = to_gemini_bundle(specs)
        elif resolved == "ollama":
            from opentools.adapters.models.ollama.bundle import to_ollama_bundle

            bundle = to_ollama_bundle(specs)
        elif resolved == "openrouter":
            from opentools.adapters.models.openrouter.bundle import (
                to_openrouter_bundle,
            )

            bundle = to_openrouter_bundle(specs)
        else:
            # should never be reached -- but in case
            raise ValueError(f"Unknown model: {resolved}")

        self._bundle_cache[key] = bundle
        return bundle

    @property
    def tools(self) -> list[Any]:
        return self.bundle().tools

    async def call_tool(self, tool_name: str, tool_input: ToolInput) -> Any:
        return await self.bundle().call(tool_name, tool_input)

    def __iter__(self) -> Iterator[Any]:
        return iter(self.tools)
