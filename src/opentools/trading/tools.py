from __future__ import annotations

from typing import Any, Iterable, Literal

from opentools.core.tools import ToolSpec

ProviderName = Literal["alpaca"]


def tools_for_trading(
    services: dict[ProviderName, Any],
    *,
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
) -> list[ToolSpec]:
    include_set = set(include or [])
    exclude_set = set(exclude or [])

    out: list[ToolSpec] = []

    for provider, svc in services.items():
        if provider == "alpaca":
            from opentools.trading.providers.alpaca.tools import alpaca_tools

            out.extend(alpaca_tools(svc))
        else:
            raise ValueError(f"Unknown trading provider: {provider}")

    if include_set:
        out = [t for t in out if t.name in include_set]
    if exclude_set:
        out = [t for t in out if t.name not in exclude_set]

    return out
