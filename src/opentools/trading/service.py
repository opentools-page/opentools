from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Iterator, Literal, Protocol

from opentools.core.tools import ToolBundle, ToolInput, ToolSpec

from .schemas import Account, Clock, Position

ModelName = Literal["anthropic", "openai"]


class TradingProviderClient(Protocol):
    provider: str

    async def get_account(self) -> dict: ...
    async def list_positions(self) -> list[dict]: ...
    async def get_clock(self) -> dict: ...


@dataclass
class TradingService(Iterable[Any]):
    """
    Neutral trading domain service + tool surface.

    Neutral core:
      - get_account()      -> Account
      - list_positions()   -> list[Position]
      - get_clock()        -> Clock

    Tool surface (model-aware, but framework-agnostic):
      - tools              -> provider-ready tool list for the configured model
      - bundle(...)        -> ToolBundle (tools + dispatch + call helper)
      - call_tool(...)     -> run a tool by sanitized name
      - iterable           -> can be passed directly as `tools=svc`
    """

    client: TradingProviderClient
    account_mapper: Callable[[dict], Account]
    position_mapper: Callable[[dict], Position | None]
    clock_mapper: Callable[[dict], Clock]

    # REQUIRED: model name to be provided on instantiation
    model: ModelName

    _bundle_cache: dict[
        tuple[ModelName, tuple[str, ...], tuple[str, ...]], ToolBundle
    ] = field(default_factory=dict, init=False, repr=False)

    @property
    def provider(self) -> str:
        return getattr(self.client, "provider", "unknown")

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

    async def get_clock(self) -> Clock:
        raw = await self.client.get_clock()
        return self.clock_mapper(raw)

    def tool_specs(
        self,
        *,
        include: Iterable[str] | None = None,
        exclude: Iterable[str] | None = None,
    ) -> list[ToolSpec]:
        """
        Return neutral ToolSpecs.
        """
        include_set = set(include or [])
        exclude_set = set(exclude or [])

        if self.provider == "alpaca":
            from opentools.trading.providers.alpaca.tools import alpaca_tools

            specs = alpaca_tools(self)
        else:
            raise ValueError(f"Unknown trading provider: {self.provider}")

        if include_set:
            specs = [t for t in specs if t.name in include_set]
        if exclude_set:
            specs = [t for t in specs if t.name not in exclude_set]
        return specs

    def bundle(
        self,
        *,
        include: Iterable[str] | None = None,
        exclude: Iterable[str] | None = None,
        model: ModelName | None = None,
    ) -> ToolBundle:
        """
        Build (or reuse cached) ToolBundle for a given model + filter set.
        """
        resolved: ModelName = model or self.model

        inc = tuple(sorted(set(include or ())))
        exc = tuple(sorted(set(exclude or ())))

        key = (resolved, inc, exc)
        if key in self._bundle_cache:
            return self._bundle_cache[key]

        specs = self.tool_specs(include=inc, exclude=exc)

        if resolved == "anthropic":
            from opentools.adapters.anthropic.bundle import to_anthropic_bundle

            bundle = to_anthropic_bundle(list(specs))
        elif resolved == "openai":
            from opentools.adapters.openai import to_openai_bundle

            bundle = to_openai_bundle(specs)
        else:
            raise ValueError(f"Unknown model: {resolved}")

        self._bundle_cache[key] = bundle
        return bundle

    @property
    def tools(self) -> list[Any]:
        """
        Provider-ready tools list for the configured model.

        This is what you pass to:
          - Anthropic: tools=svc.tools or tools=svc
          - OpenAI:    tools=/functions=/tools depending on client
        """
        return self.bundle().tools

    async def call_tool(self, tool_name: str, tool_input: ToolInput) -> Any:
        """
        Run a tool by its sanitised name.
        """
        return await self.bundle().call(tool_name, tool_input)

    def __iter__(self) -> Iterator[Any]:
        """
        Allow passing the service directly as `tools=svc`.
        """
        return iter(self.tools)
