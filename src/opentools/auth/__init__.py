from __future__ import annotations

from typing import Any

from .impl import BearerTokenAuth, HeaderAuth
from .interfaces import Auth


def normalize_auth(auth: Any) -> Auth:
    # auth="TOKEN" -> Bearer token
    if isinstance(auth, str):
        return BearerTokenAuth(auth)

    # auth={"Header": "Value"}
    if isinstance(auth, dict):
        return HeaderAuth(auth)

    # otherwise assume it already implements Auth
    return auth
