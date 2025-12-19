from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Optional

ErrorKind = Literal[
    "auth",
    "rate_limit",
    "not_found",
    "validation",
    "provider",
    "transient",
]


@dataclass
class OpenToolsError(Exception):
    """
    Base error for all Opentools exceptions.
    """

    kind: ErrorKind
    message: str

    domain: Optional[str] = None
    provider: Optional[str] = None

    status_code: Optional[int] = None
    request_id: Optional[str] = None

    details: Any = None

    def __str__(self) -> str:
        bits = [self.kind, self.message]
        if self.domain:
            bits.append(f"domain={self.domain}")
        if self.provider:
            bits.append(f"provider={self.provider}")
        if self.status_code is not None:
            bits.append(f"status={self.status_code}")
        if self.request_id:
            bits.append(f"request_id={self.request_id}")
        return " | ".join(bits)


@dataclass
class AuthError(OpenToolsError):
    kind: ErrorKind = field(default="auth", init=False)
    missing_scopes: Optional[list[str]] = None


@dataclass
class RateLimitError(OpenToolsError):
    kind: ErrorKind = field(default="rate_limit", init=False)
    retry_after_s: Optional[float] = None


@dataclass
class NotFoundError(OpenToolsError):
    kind: ErrorKind = field(default="not_found", init=False)
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None


@dataclass
class ValidationError(OpenToolsError):
    kind: ErrorKind = field(default="validation", init=False)
    field_errors: Optional[list[dict[str, Any]]] = None


@dataclass
class ProviderError(OpenToolsError):
    kind: ErrorKind = field(default="provider", init=False)


@dataclass
class TransientError(OpenToolsError):
    kind: ErrorKind = field(default="transient", init=False)
