from __future__ import annotations

from typing import Any

from pydantic import BaseModel

_INTERNAL_PREFIXES: tuple[str, ...] = ("_opentools_",)
_DROP_KEYS = frozenset({"provider", "provider_fields"})


def minimal(obj: Any, *, minimal: bool) -> Any:
    seen: set[int] = set()

    def _walk(x: Any) -> Any:
        xid = id(x)
        if xid in seen:
            return "<recursion>"

        if isinstance(x, BaseModel):
            seen.add(xid)

            model_out: dict[str, Any] = {}
            for name in type(x).model_fields:
                if minimal and name in _DROP_KEYS:
                    continue
                model_out[name] = _walk(getattr(x, name))

            seen.remove(xid)
            return model_out

        if isinstance(x, dict):
            dict_out: dict[str, Any] = {}

            for k, v in x.items():
                if isinstance(k, str) and k.startswith(_INTERNAL_PREFIXES):
                    continue
                if minimal and k in _DROP_KEYS:
                    continue
                dict_out[k] = _walk(v)

            return dict_out

        if isinstance(x, list):
            return [_walk(v) for v in x]

        if isinstance(x, tuple):
            return tuple(_walk(v) for v in x)

        return x

    return _walk(obj)
