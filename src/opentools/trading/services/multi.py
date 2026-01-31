from __future__ import annotations

import warnings
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, field
from typing import Any

from opentools.core.bundles import cached_bundle_for
from opentools.core.errors import ValidationError
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

    def _normalize_tool_filter(self, x: Iterable[str] | None) -> set[str]:
        # protect against include="get_account" -> {'g','e','t',...}
        if x is None:
            return set()
        if isinstance(x, str):
            return {x}
        return {str(i) for i in x}

    def _config_is_strict(self) -> bool:
        # If ANY service considers config fatal, Multi should treat it as strict too.
        return any("config" in svc.fatal_tool_error_kinds for svc in self.services)

    def _handle_invalid_tool_names(
        self,
        *,
        kind: str,
        invalid: set[str],
        available: set[str],
    ) -> None:
        if not invalid:
            return

        msg = (
            f"Invalid tool name(s) in {kind} for provider={self.provider}: {sorted(invalid)}. "
            f"Available tools: {sorted(available)}"
        )

        if self._config_is_strict():
            raise ValidationError(
                message=msg,
                domain="trading",
                provider=self.provider,
                field_errors=[
                    {
                        "loc": [kind],
                        "msg": "invalid tool name(s)",
                        "type": "value_error.invalid",
                    }
                ],
            )

        warnings.warn(msg, category=UserWarning, stacklevel=3)

    def tool_specs(
        self,
        *,
        include: Iterable[str] | None = None,
        exclude: Iterable[str] | None = None,
    ) -> list[ToolSpec]:
        effective_include = self._normalize_tool_filter(include) or set(self.include)
        effective_exclude = self._normalize_tool_filter(exclude) or set(self.exclude)

        specs: list[ToolSpec] = []
        for svc in self.services:
            # let each service validate its own include/exclude policy internally
            specs.extend(svc.tool_specs())

        available = {t.name for t in specs}

        # Multi-level validation: include/exclude names must exist in merged set
        invalid_inc = (effective_include - available) if effective_include else set()
        invalid_exc = (effective_exclude - available) if effective_exclude else set()

        self._handle_invalid_tool_names(
            kind="include", invalid=invalid_inc, available=available
        )
        self._handle_invalid_tool_names(
            kind="exclude", invalid=invalid_exc, available=available
        )

        # In non-strict mode, just drop invalid names and continue
        if effective_include:
            effective_include = effective_include & available
            specs = [t for t in specs if t.name in effective_include]
        if effective_exclude:
            effective_exclude = effective_exclude & available
            specs = [t for t in specs if t.name not in effective_exclude]

        # Optional: if filtering nukes all tools, warn/raise too
        if (effective_include or effective_exclude) and not specs:
            msg = (
                f"Tool filtering produced zero tools for provider={self.provider}. "
                f"include={sorted(effective_include)} exclude={sorted(effective_exclude)}"
            )
            if self._config_is_strict():
                raise ValidationError(
                    message=msg,
                    domain="trading",
                    provider=self.provider,
                    field_errors=[
                        {
                            "loc": ["include/exclude"],
                            "msg": "no tools selected",
                            "type": "value_error.invalid",
                        }
                    ],
                )
            warnings.warn(msg, category=UserWarning, stacklevel=3)

        return specs

    def bundle(
        self,
        *,
        include: Iterable[str] | None = None,
        exclude: Iterable[str] | None = None,
        model: ModelName | None = None,
    ) -> ToolBundle:
        resolved = model or self.model

        effective_include = tuple(
            sorted(self._normalize_tool_filter(include) or set(self.include))
        )
        effective_exclude = tuple(
            sorted(self._normalize_tool_filter(exclude) or set(self.exclude))
        )

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
        if not isinstance(other, (TradingService, MultiTradingService)):
            return NotImplemented  # type: ignore[return-value]
        return combine(self, other)

    def __radd__(self, other: Any) -> "MultiTradingService":
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
