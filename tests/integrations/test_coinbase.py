from __future__ import annotations

import json

import pytest

from ..helpers.asserts import assert_minimal_contract
from ..helpers.dump import dump_full, dump_minimal

pytestmark = pytest.mark.integration


def _debug_print(title: str, changed: list[str], removed: list[str]) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
    print(json.dumps({"changed_paths": changed, "removed_paths": removed}, indent=2))


@pytest.mark.asyncio
async def test_coinbase_service(coinbase_service):
    s = coinbase_service

    # account
    acct = await s.get_account()
    assert acct is not None
    assert getattr(acct, "provider", None) in (None, "coinbase")

    assert_minimal_contract(
        dump_full(acct),
        dump_minimal(acct),
        must_remove=["provider", "provider_fields"],
    )

    # accounts
    accounts = await s.list_accounts(limit=5)
    assert isinstance(accounts, list)
    assert len(accounts) >= 1
    assert getattr(accounts[0], "id", None)

    assert_minimal_contract(
        dump_full(accounts),
        dump_minimal(accounts),
        must_remove=["[0].provider", "[0].provider_fields"],
    )

    # portfolios
    portfolios = await s.list_portfolios()
    assert isinstance(portfolios, list)
    assert len(portfolios) >= 1

    pid = getattr(portfolios[0], "id", None)
    assert pid, "Expected first portfolio to have an id"

    bd = await s.get_portfolio_breakdown(portfolio_uuid=str(pid))
    assert bd is not None

    assert_minimal_contract(
        dump_full(bd),
        dump_minimal(bd),
        must_remove=[
            "provider",
            "provider_fields",
            "balances.provider_fields",
            "portfolio.provider",
            "portfolio.provider_fields",
        ],
    )

    # positions
    positions = await s.list_positions()
    assert isinstance(positions, list)
    if positions:
        assert getattr(positions[0], "symbol", None)
        assert_minimal_contract(
            dump_full(positions),
            dump_minimal(positions),
            must_remove=["[0].provider", "[0].provider_fields"],
        )

    # assets
    assets = await s.list_assets(limit=5)
    assert isinstance(assets, list)
    if assets:
        assert getattr(assets[0], "symbol", None)
        assert_minimal_contract(
            dump_full(assets),
            dump_minimal(assets),
            must_remove=["[0].provider", "[0].provider_fields"],
        )

        first_id = getattr(assets[0], "id", None) or getattr(assets[0], "symbol", None)
        assert first_id
        a = await s.get_asset(str(first_id))
        assert a is not None
        assert_minimal_contract(
            dump_full(a),
            dump_minimal(a),
            must_remove=["provider", "provider_fields"],
        )

    # orders
    orders = await s.list_orders(limit=5, status=None)
    assert isinstance(orders, list)
    if orders:
        assert getattr(orders[0], "id", None)
        assert_minimal_contract(
            dump_full(orders),
            dump_minimal(orders),
            must_remove=["[0].provider", "[0].provider_fields"],
        )

        o = await s.get_order(str(orders[0].id))
        assert o is not None
        assert_minimal_contract(
            dump_full(o),
            dump_minimal(o),
            must_remove=["provider", "provider_fields"],
        )
