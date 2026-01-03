from __future__ import annotations

from typing import Any


def _is_primitive(x: Any) -> bool:
    return x is None or isinstance(x, (str, int, float, bool))


def diff_paths(full: Any, minimal: Any, path: str = "") -> tuple[list[str], list[str]]:
    changed: list[str] = []
    removed: list[str] = []

    if isinstance(full, dict) and isinstance(minimal, dict):
        for k in full.keys():
            p = f"{path}.{k}" if path else str(k)
            if k not in minimal:
                removed.append(p)
            else:
                c, r = diff_paths(full[k], minimal[k], p)
                changed.extend(c)
                removed.extend(r)

        return changed, removed

    if isinstance(full, list) and isinstance(minimal, list):
        n = min(len(full), len(minimal))
        for i in range(n):
            p = f"{path}[{i}]" if path else f"[{i}]"
            c, r = diff_paths(full[i], minimal[i], p)
            changed.extend(c)
            removed.extend(r)
        return changed, removed

    if _is_primitive(full) and _is_primitive(minimal):
        if full is not minimal:
            changed.append(path or "<root>")
        return changed, removed

    if type(full) is not type(minimal):
        changed.append(path or "<root>")
        return changed, removed

    if full is not minimal:
        changed.append(path or "<root>")
    return changed, removed
