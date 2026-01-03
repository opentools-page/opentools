from __future__ import annotations

from opentools.core.errors import (
    AuthError,
    NotFoundError,
    ProviderError,
    RateLimitError,
    TransientError,
    ValidationError,
)


def raise_for_status(
    *,
    status_code: int,
    text: str,
    domain: str,
    provider: str,
    request_id: str | None = None,
    retry_after_s: float | None = None,
) -> None:
    if status_code in (401, 403):
        raise AuthError(
            message="Unauthorised (check API keys / permissions)",
            domain=domain,
            provider=provider,
            status_code=status_code,
            request_id=request_id,
            details=text,
        )

    if status_code == 404:
        raise NotFoundError(
            message="Resource not found",
            domain=domain,
            provider=provider,
            status_code=status_code,
            request_id=request_id,
            details=text,
        )

    if status_code in (400, 422):
        raise ValidationError(
            message="Invalid parameters for provider",
            domain=domain,
            provider=provider,
            status_code=status_code,
            request_id=request_id,
            details=text,
        )

    if status_code == 429:
        raise RateLimitError(
            message="Rate limited by provider",
            domain=domain,
            provider=provider,
            status_code=status_code,
            request_id=request_id,
            retry_after_s=retry_after_s,
            details=text,
        )

    if status_code >= 500:
        raise TransientError(
            message="Provider server error",
            domain=domain,
            provider=provider,
            status_code=status_code,
            request_id=request_id,
            details=text,
        )

    if status_code >= 400:
        raise ProviderError(
            message="Provider request failed",
            domain=domain,
            provider=provider,
            status_code=status_code,
            request_id=request_id,
            details=text,
        )
