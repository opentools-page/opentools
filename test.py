from __future__ import annotations

import asyncio
import json
import os
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel

from opentools import trading

# pretty print helpers


def _json_default(x: Any) -> Any:
    # Make JSON stable/readable without changing semantics.
    if isinstance(x, datetime):
        return x.isoformat()
    if isinstance(x, date):
        return x.isoformat()
    if isinstance(x, Decimal):
        return str(x)
    if isinstance(x, BaseModel):
        return x.model_dump()
    return str(x)


def _pretty(title: str, obj: Any) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(
        json.dumps(
            obj,
            indent=2,
            sort_keys=True,  # stable ordering = easier diffs
            default=_json_default,
        )
    )


# dump helpers


def _dump_full(obj: Any) -> Any:
    """
    FULL output: reflect the model's real serialized representation.
    No key-dropping, no recursion tricks, no cleanup.
    """
    if isinstance(obj, list):
        return [_dump_full(x) for x in obj]
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    return obj


def _dump_minimal(obj: Any) -> Any:
    """
    MINIMAL output: reflect exactly what the models provide for 'minimal'
    today (top-level canonical_view or top-level key pop fallback).
    """

    if isinstance(obj, list):
        return [_dump_minimal(x) for x in obj]

    if hasattr(obj, "canonical_view"):
        return obj.canonical_view(include_provider=False, include_provider_fields=False)

    if isinstance(obj, BaseModel):
        d = obj.model_dump()
        d.pop("provider", None)
        d.pop("provider_fields", None)
        return d

    if isinstance(obj, dict):
        d = dict(obj)
        d.pop("provider", None)
        d.pop("provider_fields", None)
        return d

    return obj


def _pretty_full_and_minimal(title: str, obj: Any) -> None:
    full = _dump_full(obj)
    minimal = _dump_minimal(obj)

    _pretty(f"{title} (FULL)", full)
    _pretty(f"{title} (MINIMAL)", minimal)

    _pretty(f"{title} (DIFF SUMMARY)", _diff_summary(full, minimal))


# diff helpers for readability


def _diff_summary(full: Any, minimal: Any) -> dict[str, Any]:
    """
    Summarize differences WITHOUT changing the underlying outputs.
    Shows:
      - paths removed (present in FULL, absent in MINIMAL)
      - paths changed (same path, different value)
    """
    removed: list[str] = []
    changed: list[str] = []

    def walk(a: Any, b: Any, path: str) -> None:
        if isinstance(a, dict) and isinstance(b, dict):
            a_keys = set(a.keys())
            b_keys = set(b.keys())

            for k in sorted(a_keys - b_keys):
                removed.append(f"{path}.{k}" if path else str(k))

            for k in sorted(a_keys & b_keys):
                walk(a[k], b[k], f"{path}.{k}" if path else str(k))
            return

        if isinstance(a, list) and isinstance(b, list):
            n = min(len(a), len(b))
            if len(a) != len(b):
                changed.append(f"{path} (list length {len(a)} -> {len(b)})")
            for i in range(n):
                walk(a[i], b[i], f"{path}[{i}]")
            return

        # Base case: different primitive or type mismatch
        if a != b:
            changed.append(path or "<root>")

    walk(full, minimal, "")

    return {
        "removed_paths": removed,
        "changed_paths": changed,
    }


# main testing


async def main() -> None:
    load_dotenv()

    coinbase_key = (
        os.environ.get("COINBASE_KEY")
        or os.environ.get("COINBASE_API_KEY")
        or os.environ.get("COINBASE_API_KEY_ID")
    )
    coinbase_secret = (
        os.environ.get("COINBASE_SECRET")
        or os.environ.get("COINBASE_API_SECRET")
        or os.environ.get("COINBASE_API_SECRET_KEY")
    )

    if not coinbase_key or not coinbase_secret:
        raise RuntimeError(
            "Missing Coinbase credentials. Set COINBASE_API_KEY + COINBASE_API_SECRET "
            "(or COINBASE_KEY/COINBASE_SECRET)."
        )

    service = trading.coinbase(
        api_key=coinbase_key,
        api_secret=coinbase_secret,
        model="gemini",
        framework=None,
    )

    _pretty("Provider", {"provider": getattr(service, "provider", None)})

    acct = await service.get_account()
    _pretty_full_and_minimal("Canonical account (Account)", acct)

    accounts = await service.list_accounts(limit=5)
    _pretty_full_and_minimal("Canonical accounts (Account[])", accounts)

    portfolios = await service.list_portfolios()
    _pretty_full_and_minimal("Canonical portfolios (Portfolio[])", portfolios)

    if portfolios:
        pid = getattr(portfolios[0], "id", None)
        if pid:
            bd = await service.get_portfolio_breakdown(portfolio_uuid=str(pid))
            _pretty_full_and_minimal(
                "Canonical portfolio breakdown (PortfolioBreakdown)", bd
            )

    positions = await service.list_positions()
    _pretty_full_and_minimal("Canonical positions (Position[])", positions)

    assets = await service.list_assets(limit=5, asset_class="crypto")
    _pretty_full_and_minimal("Canonical assets (Asset[])", assets)

    if assets:
        a_sym = getattr(assets[0], "symbol", None)
        if a_sym:
            asset = await service.get_asset(str(a_sym))
            _pretty_full_and_minimal("Canonical get_asset(Asset)", asset)

    orders = await service.list_orders(limit=5, status=None)
    _pretty_full_and_minimal("Canonical orders (Order[])", orders)

    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
