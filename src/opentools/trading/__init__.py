from __future__ import annotations

from typing import Any, Iterable, Literal, Mapping

from opentools.auth.impl import AlpacaAuth, HeaderAuth
from opentools.core.errors import AuthError
from opentools.trading.providers.alpaca._endpoints import LIVE_BASE_URL, PAPER_BASE_URL
from opentools.trading.providers.alpaca.client import AlpacaClient
from opentools.trading.providers.alpaca.mappers import (
    account_from_alpaca,
    asset_from_alpaca,
    clock_from_alpaca,
    order_from_alpaca,
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
    model: ModelName = "anthropic",
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
) -> TradingService:
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

    inc_tools = tuple(sorted(set(include or ())))
    exc_tools = tuple(sorted(set(exclude or ())))

    return TradingService(
        client=client,
        account_mapper=account_from_alpaca,
        position_mapper=position_from_alpaca,
        clock_mapper=clock_from_alpaca,
        asset_mapper=asset_from_alpaca,
        order_mapper=order_from_alpaca,
        model=model,
        include=inc_tools,
        exclude=exc_tools,
    )
