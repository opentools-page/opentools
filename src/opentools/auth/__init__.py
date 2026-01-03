from __future__ import annotations

from typing import Any

from .impl import BearerTokenAuth, HeaderAuth
from .interface import Auth


def normalise_auth(auth: Any) -> Auth:
    if isinstance(auth, str):
        return BearerTokenAuth(auth)

    if isinstance(auth, dict):
        return HeaderAuth(auth)

    return auth
