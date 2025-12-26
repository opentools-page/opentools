from __future__ import annotations

from typing import Any

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
    """
    Thin HTTP wrapper over:
      GET /v2/account/portfolio/history

    All arguments are already RFC3339 / Alpaca-compatible strings or None.
    This function is deliberately dumb: it just builds query params and
    returns dict JSON via the transport.
    """
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

    path = "/v2/account/portfolio/history"
    if params:
        path = f"{path}?{'&'.join(params)}"

    return await transport.get_dict_json(path)
