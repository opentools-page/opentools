from __future__ import annotations

from tests.helpers.diff import diff_paths


def assert_minimal_contract(full_obj, minimal_obj, *, must_remove: list[str]) -> None:
    changed, removed = diff_paths(full_obj, minimal_obj)
    assert changed == [], (
        f"Minimal changed values, expected only removals. changed={changed}"
    )
    for p in must_remove:
        assert p in removed, f"Expected removed path '{p}', got removed={removed}"
