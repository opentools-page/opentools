from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from opentools.core.errors import ProviderError


@dataclass(frozen=True)
class ToolErrorView:
    kind: str | None
    message: str | None
    domain: str | None
    provider: str | None
    status_code: int | None
    request_id: str | None
    details: Any


def _as_mapping(x: Any) -> Mapping[str, Any] | None:
    return x if isinstance(x, Mapping) else None


def parse_tool_error(result: Any) -> ToolErrorView | None:
    r = _as_mapping(result)
    if not r:
        return None
    if r.get("ok") is not False:
        return None

    err = _as_mapping(r.get("error"))
    if not err:
        return None

    def _s(v: Any) -> str | None:
        return v if isinstance(v, str) else None

    def _i(v: Any) -> int | None:
        return v if isinstance(v, int) else None

    return ToolErrorView(
        kind=_s(err.get("kind")),
        message=_s(err.get("message")),
        domain=_s(err.get("domain")),
        provider=_s(err.get("provider")),
        status_code=_i(err.get("status_code")),
        request_id=_s(err.get("request_id")),
        details=err.get("details"),
    )


def is_tool_error(result: Any) -> bool:
    return parse_tool_error(result) is not None


def is_fatal_tool_error(
    result: Any,
    *,
    fatal_kinds: Sequence[str] = ("auth", "config"),
) -> bool:
    view = parse_tool_error(result)
    if view is None:
        return False
    return (view.kind or "") in set(fatal_kinds)


def raise_if_fatal_tool_error(
    result: Any,
    *,
    fatal_kinds: Sequence[str] = ("auth", "config"),
) -> None:
    if not is_fatal_tool_error(result, fatal_kinds=fatal_kinds):
        return

    view = parse_tool_error(result)
    assert view is not None

    raise ProviderError(
        message=view.message or "Tool failed",
        domain=view.domain or "tool",
        provider=view.provider or "unknown",
        status_code=view.status_code,
        request_id=view.request_id,
        details=view.details,
    )
