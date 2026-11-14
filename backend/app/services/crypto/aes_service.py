"""AES-256-GCM wrapper for Crypto Lab contrast with the didactic SPN."""

from __future__ import annotations

import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_SIZE = 12


def encrypt(plaintext: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    """Return nonce || ciphertext+tag."""
    if len(key) != 32:
        raise ValueError("AES-256-GCM key must be 32 bytes")
    nonce = os.urandom(NONCE_SIZE)
    aesgcm = AESGCM(key)
    ct = aesgcm.encrypt(nonce, plaintext, aad)
    return nonce + ct


def decrypt(blob: bytes, key: bytes, *, aad: bytes | None = None) -> bytes:
    if len(key) != 32:
        raise ValueError("AES-256-GCM key must be 32 bytes")
    if len(blob) < NONCE_SIZE + 16:
        raise ValueError("Invalid AES-GCM ciphertext")
    nonce, ct = blob[:NONCE_SIZE], blob[NONCE_SIZE:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct, aad)
