from __future__ import annotations

import re

_ALLOWED = re.compile(r"[^a-zA-Z0-9_-]+")
_REPEAT = re.compile(r"[-_]{2,}")


def sanitize_tool_name(name: str, *, max_len: int = 128) -> str:
    name = name.replace(".", "_")
    name = _ALLOWED.sub("_", name)
    name = _REPEAT.sub("_", name).strip("_-")

    if not name:
        name = "tool"

    if name[0].isdigit():
        name = f"tool_{name}"

    if len(name) > max_len:
        name = name[:max_len].rstrip("_-")

    return name


def unique_name(base: str, used: set[str], *, max_len: int = 128) -> str:
    if base not in used:
        used.add(base)
        return base

    i = 2
    while True:
        suffix = f"_{i}"
        candidate = base[: max_len - len(suffix)] + suffix
        if candidate not in used:
            used.add(candidate)
            return candidate
        i += 1
