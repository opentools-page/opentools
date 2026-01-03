from __future__ import annotations

import pytest

from ..helpers.asserts import assert_minimal_contract
from ..helpers.dump import dump_full, dump_minimal

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_alpaca_service(alpaca_service):
    s = alpaca_service

    # account
    acct = await s.get_account()
    assert acct is not None
    assert getattr(acct, "provider", None) in (None, "alpaca")

    assert_minimal_contract(
        dump_full(acct),
        dump_minimal(acct),
        must_remove=["provider", "provider_fields"],
    )

    # clock
    clock = await s.get_clock()
    assert clock is not None
    assert_minimal_contract(
        dump_full(clock),
        dump_minimal(clock),
        must_remove=["provider", "provider_fields"],
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

    # portfolio history
    hist = await s.get_portfolio_history(period="1M", timeframe="1D")
    assert hist is not None
    assert_minimal_contract(
        dump_full(hist),
        dump_minimal(hist),
        must_remove=["provider", "provider_fields"],
    )

    pts = getattr(hist, "points", None)
    assert pts is not None and isinstance(pts, list)
