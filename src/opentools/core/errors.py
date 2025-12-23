from __future__ import annotations

import json
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

    # raw provider payload, extra context, etc.
    details: Any = None

    def __str__(self) -> str:
        """
        Short, single-line summary for tracebacks.

        Full provider payload lives in `.details`, not in the message,
        so the traceback doesn't become a JSON crime scene.
        """
        prefix = f"[opentools:{self.kind}]"
        msg = str(self.message)

        meta: list[str] = []
        if self.domain:
            meta.append(f"domain={self.domain}")
        if self.provider:
            meta.append(f"provider={self.provider}")
        if self.status_code is not None:
            meta.append(f"status={self.status_code}")
        if self.request_id:
            meta.append(f"request_id={self.request_id}")

        if meta:
            return f"{prefix} {msg} ({', '.join(meta)})"
        return f"{prefix} {msg}"

    def pretty(self) -> str:
        """
        Optional: rich, multi-line formatting with details.
        """
        base = str(self)
        if self.details in (None, ""):
            return base

        try:
            details_str = json.dumps(self.details, indent=2, default=str)
        except TypeError:
            details_str = repr(self.details)

        indented = "\n    ".join(details_str.splitlines())
        return f"{base}\n  details:\n    {indented}"


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
