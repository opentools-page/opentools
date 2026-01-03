from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv

from opentools import trading

load_dotenv()


def _required_env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        pytest.skip(f"Missing env var: {name}")
    return v


@pytest.fixture
def coinbase_creds() -> tuple[str, str]:
    return _required_env("COINBASE_KEY"), _required_env("COINBASE_SECRET")


@pytest.fixture
def alpaca_creds() -> tuple[str, str]:
    return _required_env("ALPACA_KEY"), _required_env("ALPACA_SECRET")


@pytest.fixture
def coinbase_service(coinbase_creds):
    key, secret = coinbase_creds
    return trading.coinbase(
        api_key=key,
        api_secret=secret,
        model="gemini",
        framework=None,
        # coinbase defaults LIVE
    )


@pytest.fixture
def alpaca_service(alpaca_creds):
    key, secret = alpaca_creds
    return trading.alpaca(
        api_key=key,
        api_secret=secret,
        model="gemini",
        framework=None,
        # alpaca defaults PAPER
    )
