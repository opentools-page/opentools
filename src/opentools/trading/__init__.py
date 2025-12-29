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
    position_from_coinbase,
)
from opentools.trading.providers.coinbase.transport import CoinbaseTransport
from opentools.trading.services import TradingService


# alpaca
def _resolve_alpaca_auth(
    *,
    auth: Any | None,
    api_key: str | None,
    api_secret: str | None,
) -> AlpacaAuth:
    if api_key and api_secret:
        return AlpacaAuth(key_id=api_key, secret_key=api_secret)

    if isinstance(auth, AlpacaAuth):
        return auth

    if auth is not None:
        raise AuthError(
            message=(
                "Invalid Alpaca auth object. Only two patterns are supported: "
                "api_key + api_secret, or an explicit AlpacaAuth instance."
            ),
            domain="trading",
            provider="alpaca",
            details=repr(auth),
        )

    raise AuthError(
        message="Missing Alpaca auth. Provide api_key+api_secret.",
        domain="trading",
        provider="alpaca",
    )


def alpaca(
    *,
    api_key: str | None = None,
    api_secret: str | None = None,
    auth: Any | None = None,
    paper: bool = True,
    timeout: float = 30.0,
    model: ModelName,
    framework: FrameworkName | None = None,
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
    minimal: bool = False,
) -> TradingService:
    base_url = ALPACA_PAPER_URL if paper else ALPACA_LIVE_URL
    env = "paper" if paper else "live"

    alpaca_auth = _resolve_alpaca_auth(
        auth=auth,
        api_key=api_key,
        api_secret=api_secret,
    )

    transport = AlpacaTransport(
        auth=alpaca_auth,
        base_url=base_url,
        timeout=timeout,
        environment=env,
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
        minimal=minimal,
    )


# coinbase
def _resolve_coinbase_auth(
    *,
    auth: Any | None,
    api_key: str | None,
    api_secret: str | None,
    bearer_token: str | None,
    host: str,
) -> Any:
    explicit_api_creds = bool(api_key or api_secret)
    explicit_bearer = bool(bearer_token)

    if explicit_api_creds and explicit_bearer:
        raise AuthError(
            message=(
                "Ambiguous Coinbase auth configuration: both api_key/api_secret and "
                "bearer_token were provided. Use either PEM-backed api_key + api_secret "
                "or a pre-built bearer_token, not both."
            ),
            domain="trading",
            provider="coinbase",
            details={
                "has_api_key": bool(api_key),
                "has_api_secret": bool(api_secret),
                "has_bearer_token": bool(bearer_token),
            },
        )

    if explicit_api_creds:
        if not (api_key and api_secret):
            raise AuthError(
                message=(
                    "Incomplete Coinbase credentials: both api_key and api_secret "
                    "(the PEM private key) are required."
                ),
                domain="trading",
                provider="coinbase",
                details={
                    "has_api_key": bool(api_key),
                    "has_api_secret": bool(api_secret),
                },
            )

        return CoinbaseAuth(
            api_key=api_key,
            api_secret=api_secret,
            host=host,
        )

    if explicit_bearer:
        return BearerTokenAuth(token=bearer_token)

    if isinstance(auth, Mapping):
        if "key_name" in auth and "private_key" in auth:
            return CoinbaseAuth(
                api_key=str(auth["key_name"]),
                api_secret=str(auth["private_key"]),
                host=host,
            )

        if "api_key" in auth and "api_secret" in auth:
            return CoinbaseAuth(
                api_key=str(auth["api_key"]),
                api_secret=str(auth["api_secret"]),
                host=host,
            )

        if "Authorization" in auth:
            return HeaderAuth(headers_dict=dict(auth))

        raise AuthError(
            message=(
                "Invalid Coinbase auth mapping. Expected either "
                "{api_key, api_secret}, {key_name, private_key}, "
                "or an Authorization header."
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
        message=(
            "Missing Coinbase auth. Provide api_key+api_secret (PEM private key) "
            "or a bearer_token / Authorization header."
        ),
        domain="trading",
        provider="coinbase",
    )


def coinbase(
    *,
    auth: Any | None = None,
    api_key: str | None = None,
    api_secret: str | None = None,
    bearer_token: str | None = None,
    paper: bool = False,
    timeout: float = 30.0,
    model: ModelName,
    framework: FrameworkName | None = None,
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
    minimal: bool = False,
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

    env = "paper" if paper else "live"

    transport = CoinbaseTransport(
        auth=cb_auth,
        base_url=base_url,
        timeout=timeout,
        environment=env,
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
        model=model,
        framework=framework,
        include=inc_tools,
        exclude=exc_tools,
        minimal=minimal,
    )
