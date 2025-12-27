from __future__ import annotations

from typing import Any

from .._endpoints import PORTFOLIO_HISTORY_PATH
from ..transport import AlpacaTransport


async def get_portfolio_history(
    transport: AlpacaTransport,
    *,
    period: str | None = None,
    timeframe: str | None = None,
    intraday_reporting: str | None = None,
    start: str | None = None,
    end: str | None = None,
    pnl_reset: str | None = None,
    cashflow_types: str | None = None,
) -> dict[str, Any]:
    params: list[str] = []

    if period is not None:
        params.append(f"period={period}")
    if timeframe is not None:
        params.append(f"timeframe={timeframe}")
    if intraday_reporting is not None:
        params.append(f"intraday_reporting={intraday_reporting}")
    if start is not None:
        params.append(f"start={start}")
    if end is not None:
        params.append(f"end={end}")
    if pnl_reset is not None:
        params.append(f"pnl_reset={pnl_reset}")
    if cashflow_types is not None:
        params.append(f"cashflow_types={cashflow_types}")

    path = PORTFOLIO_HISTORY_PATH
    if params:
        path = f"{path}?{'&'.join(params)}"

    return await transport.get_dict_json(path)
