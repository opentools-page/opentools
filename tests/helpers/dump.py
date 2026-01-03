from __future__ import annotations

from typing import Any

from pydantic import BaseModel


def _dump(obj: Any, *, include_provider: bool, include_provider_fields: bool) -> Any:
    # lists/tuples
    if isinstance(obj, (list, tuple)):
        return [
            _dump(
                x,
                include_provider=include_provider,
                include_provider_fields=include_provider_fields,
            )
            for x in obj
        ]

    # dicts
    if isinstance(obj, dict):
        return {
            k: _dump(
                v,
                include_provider=include_provider,
                include_provider_fields=include_provider_fields,
            )
            for k, v in obj.items()
        }

    if hasattr(obj, "canonical_view") and callable(getattr(obj, "canonical_view")):
        return obj.canonical_view(
            include_provider=include_provider,
            include_provider_fields=include_provider_fields,
        )

    if isinstance(obj, BaseModel):
        return obj.model_dump()

    return obj


def dump_full(obj: Any) -> Any:
    return _dump(obj, include_provider=True, include_provider_fields=True)


def dump_minimal(obj: Any) -> Any:
    return _dump(obj, include_provider=False, include_provider_fields=False)
