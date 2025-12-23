from __future__ import annotations

from typing import Any, Protocol

from .types import FrameworkName


class FrameworkAwareService(Protocol):
    """
    Minimal interface for something that can be adapted to a framework.

    TradingService already satisfies this:
      - .framework: FrameworkName | None
      - .tools: list[Any]
    """

    framework: FrameworkName | None

    @property
    def tools(self) -> list[Any]: ...


def framework_tools(service: FrameworkAwareService) -> list[Any]:
    """
    Return a list of *framework-ready* tools for the given service.

    - If `service.framework is None`:
        just returns the raw `service.tools`
    - If `pydantic_ai`:
        uses adapters.frameworks.pydantic_ai.tools_for_service
    - If `langgraph`:
        uses adapters.frameworks.langgraph.tools_for_service
    - If unknown:
        raises ValueError
    """

    fw = service.framework

    if fw is None:
        # No framework declared → just use raw tool bundle tools
        return list(service.tools)

    if fw == "pydantic_ai":
        from opentools.adapters.frameworks.pydantic_ai import tools_for_service

        return list(tools_for_service(service))

    if fw == "langgraph":
        from opentools.adapters.frameworks.langgraph import (
            tools_for_service as lg_tools_for_service,
        )

        return list(lg_tools_for_service(service))

    raise ValueError(f"Unknown framework: {fw!r}")
