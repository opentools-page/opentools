from __future__ import annotations

from typing import Any, Iterable, Mapping

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
from opentools.trading.service import ModelName, TradingService


def _resolve_alpaca_auth(
    *,
    auth: Any | None,
    key_id: str | None,
    secret_key: str | None,
) -> Any:
    if key_id and secret_key:
        return AlpacaAuth(key_id=key_id, secret_key=secret_key)

    if isinstance(auth, Mapping):
        if "key_id" in auth and "secret_key" in auth:
            return AlpacaAuth(
                key_id=str(auth["key_id"]),
                secret_key=str(auth["secret_key"]),
            )

        if "APCA-API-KEY-ID" in auth and "APCA-API-SECRET-KEY" in auth:
            return HeaderAuth(headers_dict=dict(auth))

        raise AuthError(
            message=(
                "Invalid Alpaca auth mapping. Expected either "
                "{key_id, secret_key} or raw APCA-* headers."
            ),
            domain="trading",
            provider="alpaca",
            details=dict(auth),
        )

    if auth is not None:
        if isinstance(auth, (AlpacaAuth, HeaderAuth)):
            return auth

        raise AuthError(
            message=(
                "Invalid Alpaca auth object. Expected AlpacaAuth, HeaderAuth "
                "or a valid mapping / key_id+secret_key."
            ),
            domain="trading",
            provider="alpaca",
            details=repr(auth),
        )

    raise AuthError(
        message="Missing Alpaca auth. Provide key_id+secret_key or an auth mapping.",
        domain="trading",
        provider="alpaca",
    )


def alpaca(
    *,
    auth: Any | None = None,
    key_id: str | None = None,
    secret_key: str | None = None,
    paper: bool = True,
    timeout: float = 30.0,
    model: ModelName,
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
) -> TradingService:
    """
    Create a TradingService bound to Alpaca.

    The `model` parameter selects which LLM adapter bundle to produce
    ("anthropic", "openai", or "gemini" or "ollama). No default is chosen.
    """
    base_url = PAPER_BASE_URL if paper else LIVE_BASE_URL

    alpaca_auth = _resolve_alpaca_auth(
        auth=auth,
        key_id=key_id,
        secret_key=secret_key,
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
