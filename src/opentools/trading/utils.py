from __future__ import annotations

from typing import Any


def minimal(obj: Any, *, minimal: bool) -> Any:
    include_provider = not minimal
    include_provider_fields = not minimal

    if isinstance(obj, list):
        out: list[Any] = []
        for x in obj:
            if hasattr(x, "canonical_view"):
                out.append(
                    x.canonical_view(
                        include_provider=include_provider,
                        include_provider_fields=include_provider_fields,
                    )
                )
            else:
                out.append(x)
        return out

    if hasattr(obj, "canonical_view"):
        return obj.canonical_view(
            include_provider=include_provider,
            include_provider_fields=include_provider_fields,
        )

    return obj
