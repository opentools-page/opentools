from __future__ import annotations

from typing import Any, Iterable, Mapping
from urllib.parse import urlparse

from opentools.auth.impl import AlpacaAuth, BearerTokenAuth, CoinbaseAuth, HeaderAuth
from opentools.core.errors import AuthError
from opentools.core.types import FrameworkName, ModelName
from opentools.trading.providers.alpaca._endpoints import (
    ALPACA_LIVE_URL,
    ALPACA_PAPER_URL,
)
from opentools.trading.providers.alpaca.client import AlpacaClient
from opentools.trading.providers.alpaca.mappers import (
    account_from_alpaca,
    asset_from_alpaca,
    clock_from_alpaca,
    order_from_alpaca,
    portfolio_history_from_alpaca,
    position_from_alpaca,
)
from opentools.trading.providers.alpaca.transport import AlpacaTransport
from opentools.trading.providers.coinbase._endpoints import (
    COINBASE_LIVE_URL,
    COINBASE_SANDBOX_URL,
)
from opentools.trading.providers.coinbase.client import CoinbaseClient
from opentools.trading.providers.coinbase.mappers import (
    account_from_coinbase,
    asset_from_coinbase,
    clock_from_coinbase,
    order_from_coinbase,
    portfolio_history_from_coinbase,
    position_from_coinbase,
)
from opentools.trading.providers.coinbase.transport import CoinbaseTransport
from opentools.trading.services import TradingService

# -----------------
# Alpaca
# -----------------


def _resolve_alpaca_auth(
    *,
    auth: Any | None,
    api_key: str | None,
    api_secret: str | None,
    key_id: str | None,
    secret_key: str | None,
) -> Any:
    if api_key and api_secret:
        return AlpacaAuth(key_id=api_key, secret_key=api_secret)

    if key_id and secret_key:
        return AlpacaAuth(key_id=key_id, secret_key=secret_key)

    if isinstance(auth, Mapping):
        if "api_key" in auth and "api_secret" in auth:
            return AlpacaAuth(
                key_id=str(auth["api_key"]),
                secret_key=str(auth["api_secret"]),
            )

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
                "{api_key, api_secret}, {key_id, secret_key} "
                "or raw APCA-* headers."
            ),
            domain="trading",
            provider="alpaca",
            details=dict(auth),
        )

    # 3) Direct auth objects
    if auth is not None:
        if isinstance(auth, (AlpacaAuth, HeaderAuth)):
            return auth

        raise AuthError(
            message=(
                "Invalid Alpaca auth object. Expected AlpacaAuth, HeaderAuth "
                "or a valid mapping / api_key+api_secret."
            ),
            domain="trading",
            provider="alpaca",
            details=repr(auth),
        )

    raise AuthError(
        message="Missing Alpaca auth. Provide api_key+api_secret or an auth mapping.",
        domain="trading",
        provider="alpaca",
    )


def alpaca(
    *,
    auth: Any | None = None,
    api_key: str | None = None,
    api_secret: str | None = None,
    key_id: str | None = None,
    secret_key: str | None = None,
    paper: bool = True,
    timeout: float = 30.0,
    model: ModelName,
    framework: FrameworkName | None = None,
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
) -> TradingService:
    """
    Factory for an Alpaca-backed TradingService.

    Recommended usage (new-style):

        alpaca(
            api_key="...",
            api_secret="...",
            model="ollama",
        )

    """

    base_url = ALPACA_PAPER_URL if paper else ALPACA_LIVE_URL

    alpaca_auth = _resolve_alpaca_auth(
        auth=auth,
        api_key=api_key,
        api_secret=api_secret,
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
        portfolio_history_mapper=portfolio_history_from_alpaca,
        model=model,
        framework=framework,
        include=inc_tools,
        exclude=exc_tools,
    )


# Coinbase


def _resolve_coinbase_auth(
    *,
    auth: Any | None,
    api_key: str | None,
    api_secret: str | None,
    bearer_token: str | None,
    host: str,
) -> Any:
    if api_key and api_secret:
        return CoinbaseAuth(
            api_key=api_key,
            api_secret=api_secret,
            host=host,
        )

    if bearer_token:
        return BearerTokenAuth(token=bearer_token)

    if isinstance(auth, Mapping):
        if "api_key" in auth and "api_secret" in auth:
            return CoinbaseAuth(
                api_key=str(auth["api_key"]),
                api_secret=str(auth["api_secret"]),
                host=host,
            )

        # Raw "Authorization" header
        if "Authorization" in auth:
            return HeaderAuth(headers_dict=dict(auth))

        raise AuthError(
            message=(
                "Invalid Coinbase auth mapping. Expected either "
                "{api_key, api_secret} or an Authorization header."
            ),
            domain="trading",
            provider="coinbase",
            details=dict(auth),
        )

    if isinstance(auth, (CoinbaseAuth, BearerTokenAuth, HeaderAuth)):
        return auth

    if auth is not None:
        raise AuthError(
            message=(
                "Invalid Coinbase auth object. Expected CoinbaseAuth, "
                "BearerTokenAuth, HeaderAuth or a valid mapping."
            ),
            domain="trading",
            provider="coinbase",
            details=repr(auth),
        )

    raise AuthError(
        message="Missing Coinbase auth. Provide api_key+api_secret or a bearer token.",
        domain="trading",
        provider="coinbase",
    )


def coinbase(
    *,
    auth: Any | None = None,
    api_key: str | None = None,
    api_secret: str | None = None,
    bearer_token: str | None = None,
    paper: bool = True,
    timeout: float = 30.0,
    model: ModelName,
    framework: FrameworkName | None = None,
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
) -> TradingService:
    base_url = COINBASE_SANDBOX_URL if paper else COINBASE_LIVE_URL
    parsed = urlparse(base_url)
    host = parsed.netloc

    cb_auth = _resolve_coinbase_auth(
        auth=auth,
        api_key=api_key,
        api_secret=api_secret,
        bearer_token=bearer_token,
        host=host,
    )

    transport = CoinbaseTransport(
        auth=cb_auth,
        base_url=base_url,
        timeout=timeout,
    )
    client = CoinbaseClient(transport=transport)

    inc_tools = tuple(sorted(set(include or ())))
    exc_tools = tuple(sorted(set(exclude or ())))

    return TradingService(
        client=client,
        account_mapper=account_from_coinbase,
        position_mapper=position_from_coinbase,
        clock_mapper=clock_from_coinbase,
        asset_mapper=asset_from_coinbase,
        order_mapper=order_from_coinbase,
        portfolio_history_mapper=portfolio_history_from_coinbase,
        model=model,
        framework=framework,
        include=inc_tools,
        exclude=exc_tools,
    )
