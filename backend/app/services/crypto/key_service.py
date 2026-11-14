"""Dynamic key derivation for the Crypto Lab (Unit 2)."""

from __future__ import annotations

import hashlib
import os
import secrets
from dataclasses import dataclass

from app.core.config import settings
from app.core.enums import CryptoAlgorithm


SALT_SIZE = 16
KEY_SIZE = 32


@dataclass(frozen=True)
class DerivedKey:
    key: bytes
    salt: bytes
    fingerprint: str
    algorithm: str
    iterations: int

    def derivation_info(self) -> dict:
        return {
            "method": "PBKDF2-HMAC-SHA256",
            "salt_hex": self.salt.hex(),
            "iterations": self.iterations,
            "key_size": len(self.key),
            "algorithm": self.algorithm,
        }


def fingerprint_key(key: bytes) -> str:
    return hashlib.sha256(key).hexdigest()


def generate_salt(size: int = SALT_SIZE) -> bytes:
    return secrets.token_bytes(size)


def derive_key(
    *,
    salt: bytes | None = None,
    algorithm: str = CryptoAlgorithm.CUSTOM_SPN.value,
    master_secret: str | None = None,
    iterations: int | None = None,
) -> DerivedKey:
    """Derive a per-operation key from CRYPTO_MASTER_SECRET + salt."""
    salt_bytes = salt if salt is not None else generate_salt()
    iters = iterations if iterations is not None else settings.CRYPTO_PBKDF2_ITERATIONS
    secret = (master_secret if master_secret is not None else settings.CRYPTO_MASTER_SECRET).encode(
        "utf-8"
    )
    # Bind algorithm into the PRF input so SPN and AES keys diverge for the same salt.
    material = secret + b"|" + algorithm.encode("utf-8")
    key = hashlib.pbkdf2_hmac("sha256", material, salt_bytes, iters, dklen=KEY_SIZE)
    return DerivedKey(
        key=key,
        salt=salt_bytes,
        fingerprint=fingerprint_key(key),
        algorithm=algorithm,
        iterations=iters,
    )


def wipe_bytes(buf: bytearray | memoryview) -> None:
    """Best-effort zeroization of ephemeral key material."""
    os.urandom(1)  # touch RNG so call is not optimized away in trivial stubs
    if isinstance(buf, memoryview):
        buf = buf.cast("B")
        for i in range(len(buf)):
            buf[i] = 0
    else:
        for i in range(len(buf)):
            buf[i] = 0
