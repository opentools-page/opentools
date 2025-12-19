from __future__ import annotations

from typing import Any, Mapping

from opentools.auth.impl import AlpacaAuth, HeaderAuth
from opentools.core.errors import AuthError
from opentools.finance.providers.alpaca._endpoints import LIVE_BASE_URL, PAPER_BASE_URL
from opentools.finance.providers.alpaca.client import AlpacaClient
from opentools.finance.service import FinanceService


def alpaca(
    *,
    auth: Any | None = None,
    key_id: str | None = None,
    secret_key: str | None = None,
    paper: bool = True,
    timeout_s: float = 30.0,
) -> FinanceService:
    """
    Convenience constructor for Alpaca finance service.

    Accepts:
      - auth={"key_id": "...", "secret_key": "..."}  (preferred)
      - auth={"APCA-API-KEY-ID": "...", "APCA-API-SECRET-KEY": "..."}  (raw headers)
      - key_id="...", secret_key="..." (most ergonomic)
      - auth=AlpacaAuth(...) (advanced)
    """
    base_url = PAPER_BASE_URL if paper else LIVE_BASE_URL

    # 1) kwargs style
    if key_id and secret_key:
        alpaca_auth = AlpacaAuth(key_id=key_id, secret_key=secret_key)

    # 2) dict style
    elif isinstance(auth, Mapping):
        # allow friendly keys
        if "key_id" in auth and "secret_key" in auth:
            alpaca_auth = AlpacaAuth(
                key_id=str(auth["key_id"]), secret_key=str(auth["secret_key"])
            )
        # allow raw headers
        elif "APCA-API-KEY-ID" in auth and "APCA-API-SECRET-KEY" in auth:
            alpaca_auth = HeaderAuth(headers_dict=auth)
        else:
            raise AuthError(
                message="Invalid Alpaca auth mapping. Use {key_id, secret_key} or raw APCA-* headers.",
                domain="finance",
                provider="alpaca",
                details=dict(auth),
            )

    elif auth is not None:
        alpaca_auth = auth

    else:
        raise AuthError(
            message="Missing Alpaca auth. Provide key_id+secret_key or auth mapping.",
            domain="finance",
            provider="alpaca",
        )

    client = AlpacaClient(auth=alpaca_auth, base_url=base_url, timeout_s=timeout_s)
    return FinanceService(client=client)
