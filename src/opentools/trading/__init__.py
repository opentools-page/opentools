from __future__ import annotations

from typing import Any, Literal, Mapping

from opentools.auth.impl import AlpacaAuth, HeaderAuth
from opentools.core.errors import AuthError
from opentools.trading.providers.alpaca._endpoints import LIVE_BASE_URL, PAPER_BASE_URL
from opentools.trading.providers.alpaca.client import AlpacaClient
from opentools.trading.providers.alpaca.mappers import (
    account_from_alpaca,
    clock_from_alpaca,
    position_from_alpaca,
)
from opentools.trading.providers.alpaca.transport import AlpacaTransport
from opentools.trading.service import TradingService

ModelName = Literal["anthropic", "openai"]


def alpaca(
    *,
    auth: Any | None = None,
    key_id: str | None = None,
    secret_key: str | None = None,
    paper: bool = True,
    timeout: float = 30.0,
    model: ModelName,
) -> TradingService:
    """
    Construct a TradingService wired to Alpaca.

    Auth options (pick one style):

      1) Explicit kwargs:
         alpaca(key_id="...", secret_key="...", model="anthropic")

      2) Mapping:
         alpaca(auth={"key_id": "...", "secret_key": "..."}, model="openai")
         alpaca(auth={
             "APCA-API-KEY-ID": "...",
             "APCA-API-SECRET-KEY": "...",
         }, model="anthropic")

      3) Explicit auth object:
         alpaca(auth=AlpacaAuth(...), model="anthropic")
         alpaca(auth=HeaderAuth(...), model="openai")

    Args:
        auth: Mapping or auth object.
        key_id: Alpaca API key id.
        secret_key: Alpaca API secret key.
        paper: Use paper trading base URL if True, live URL if False.
        timeout: HTTP timeout in seconds.
        model: Which LLM tool adapter to use ("anthropic" or "openai").

    Returns:
        TradingService instance with:
          - neutral methods: get_account(), list_positions(), get_clock()
          - tool surface: .tools and .call_tool(...)
    """

    base_url = PAPER_BASE_URL if paper else LIVE_BASE_URL

    if key_id and secret_key:
        alpaca_auth = AlpacaAuth(key_id=key_id, secret_key=secret_key)

    elif isinstance(auth, Mapping):
        if "key_id" in auth and "secret_key" in auth:
            alpaca_auth = AlpacaAuth(
                key_id=str(auth["key_id"]),
                secret_key=str(auth["secret_key"]),
            )
        elif "APCA-API-KEY-ID" in auth and "APCA-API-SECRET-KEY" in auth:
            alpaca_auth = HeaderAuth(headers_dict=auth)
        else:
            raise AuthError(
                message=(
                    "Invalid Alpaca auth mapping. Use {key_id, secret_key} "
                    "or raw APCA-* headers."
                ),
                domain="trading",
                provider="alpaca",
                details=dict(auth),
            )

    elif auth is not None:
        alpaca_auth = auth

    else:
        raise AuthError(
            message="Missing Alpaca auth. Provide key_id+secret_key or auth mapping.",
            domain="trading",
            provider="alpaca",
        )

    transport = AlpacaTransport(
        auth=alpaca_auth,
        base_url=base_url,
        timeout=timeout,
    )
    client = AlpacaClient(transport=transport)

    return TradingService(
        client=client,
        account_mapper=account_from_alpaca,
        position_mapper=position_from_alpaca,
        clock_mapper=clock_from_alpaca,
        model=model,
    )
