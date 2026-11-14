"""Shared Crypto Lab guards (authz already on routers; this enforces lab policy)."""

from __future__ import annotations

from app.core.config import settings
from app.core.exceptions import AppError, ForbiddenError


def ensure_crypto_lab_enabled() -> None:
    if not settings.CRYPTO_LAB_ENABLED:
        raise ForbiddenError("Crypto Lab is disabled")


def enforce_plaintext_size(data: bytes | str, *, label: str = "payload") -> None:
    size = len(data.encode("utf-8")) if isinstance(data, str) else len(data)
    limit = settings.CRYPTO_MAX_PLAINTEXT_BYTES
    if size > limit:
        raise AppError(
            f"{label} exceeds CRYPTO_MAX_PLAINTEXT_BYTES ({limit})",
            status_code=400,
        )


def enforce_cover_size(data: bytes) -> None:
    limit = settings.STEGO_MAX_COVER_BYTES
    if len(data) > limit:
        raise AppError(
            f"Cover/stego file exceeds STEGO_MAX_COVER_BYTES ({limit})",
            status_code=400,
        )


def clamp_searchable_bits(bits: int) -> int:
    max_bits = settings.CRYPTO_LAB_MAX_SEARCHABLE_BITS
    if bits < 1 or bits > max_bits:
        raise AppError(
            f"searchable_bits must be between 1 and {max_bits}",
            status_code=400,
        )
    return bits
