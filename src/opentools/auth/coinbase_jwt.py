from __future__ import annotations

import secrets
import time
from typing import Any

import jwt
from cryptography.hazmat.primitives import serialization


def build_coinbase_jwt(
    *,
    key_name: str,
    key_secret: str,
    method: str,
    host: str,
    path: str,
    expires_in: int = 120,
) -> str:
    pem_str = key_secret.replace("\\n", "\n").strip()

    private_key: Any = serialization.load_pem_private_key(
        pem_str.encode("utf-8"),
        password=None,
    )

    now = int(time.time())
    uri = f"{method.upper()} {host}{path}"

    payload: dict[str, Any] = {
        "sub": key_name,
        "iss": "cdp",
        "nbf": now,
        "exp": now + int(expires_in),
        "uri": uri,
    }

    headers: dict[str, Any] = {
        "kid": key_name,
        "nonce": secrets.token_hex(),
    }

    token = jwt.encode(
        payload,
        key=private_key,
        algorithm="ES256",
        headers=headers,
    )
    return token
