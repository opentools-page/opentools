from __future__ import annotations

from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from typing import Any

from opentools.core.bundles import cached_bundle_for
from opentools.core.tools import ToolBundle, ToolInput, ToolSpec
from opentools.core.types import FrameworkName, ModelName

from .core import TradingService


@dataclass
class MultiTradingService(Sequence[Any]):
    services: tuple[TradingService, ...]
    model: ModelName
    framework: FrameworkName | None = None
    include: tuple[str, ...] = field(default_factory=tuple)
    exclude: tuple[str, ...] = field(default_factory=tuple)

    _bundle_cache: dict[
        tuple[ModelName, tuple[str, ...], tuple[str, ...]], ToolBundle
    ] = field(default_factory=dict, init=False, repr=False)

    @property
    def provider(self) -> str:
        providers = {svc.provider for svc in self.services}
        return ",".join(sorted(providers))

    def tool_specs(
        self,
        *,
        include: Iterable[str] | None = None,
        exclude: Iterable[str] | None = None,
    ) -> list[ToolSpec]:
        effective_include = set(include or self.include)
        effective_exclude = set(exclude or self.exclude)

        specs: list[ToolSpec] = []
        for svc in self.services:
            specs.extend(svc.tool_specs())

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

    def __add__(
        self, other: TradingService | MultiTradingService
    ) -> MultiTradingService:
        from .multi import combine  # runtime import

        if not isinstance(other, (TradingService, MultiTradingService)):
            return NotImplemented  # type: ignore[return-value]
        return combine(self, other)

    def __radd__(self, other: Any) -> MultiTradingService:
        from .multi import combine  # runtime import

        if other == 0:
            return combine(self)
        if isinstance(other, (TradingService, MultiTradingService)):
            return combine(other, self)
        return NotImplemented  # type: ignore[return-value]


def combine(*services: TradingService | MultiTradingService) -> MultiTradingService:
    flat: list[TradingService] = []
    model: ModelName | None = None
    framework: FrameworkName | None = None

    for svc in services:
        if isinstance(svc, MultiTradingService):
            inner = svc.services
        else:
            inner = (svc,)

        for s in inner:
            if model is None:
                model = s.model
            elif s.model != model:
                raise ValueError(
                    f"Cannot combine TradingService with different models: "
                    f"{model!r} vs {s.model!r}"
                )

            if s.framework is not None:
                if framework is None:
                    framework = s.framework
                elif framework != s.framework:
                    raise ValueError(
                        f"Cannot combine TradingService with different frameworks: "
                        f"{framework!r} vs {s.framework!r}"
                    )

            flat.append(s)

    if not flat:
        raise ValueError("combine() requires at least one TradingService")

    return MultiTradingService(
        services=tuple(flat),
        model=model,  # type: ignore[arg-type]
        framework=framework,
    )
