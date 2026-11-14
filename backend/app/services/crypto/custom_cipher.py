"""
Didactic custom SPN cipher (Unit 2).

Structure per round (confusion + diffusion):
  1. Substitution (S-box)
  2. Permutation (byte P-box)
  3. XOR with round key

Not intended for production confidentiality — educational contrast to AES-GCM.
"""

from __future__ import annotations

import hashlib
import struct

BLOCK_SIZE = 16
NUM_ROUNDS = 8
VERSION = 1


def _build_sbox() -> tuple[list[int], list[int]]:
    # Fixed didactic S-box derived from a public constant (not a secret).
    seed = hashlib.sha256(b"SecureRecruit-SPN-SBOX-v1").digest()
    sbox = list(range(256))
    # Fisher–Yates with deterministic PRNG from seed
    state = list(seed)
    idx = 0

    def rnd() -> int:
        nonlocal idx, state
        if idx >= len(state):
            state = list(hashlib.sha256(bytes(state)).digest())
            idx = 0
        value = state[idx]
        idx += 1
        return value

    for i in range(255, 0, -1):
        j = rnd() % (i + 1)
        sbox[i], sbox[j] = sbox[j], sbox[i]

    inv = [0] * 256
    for i, v in enumerate(sbox):
        inv[v] = i
    return sbox, inv


SBOX, INV_SBOX = _build_sbox()

# Byte permutation within a 16-byte block (P-box)
PBOX = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]
INV_PBOX = [0] * 16
for _i, _p in enumerate(PBOX):
    INV_PBOX[_p] = _i


def _pkcs7_pad(data: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    if pad_len == 0:
        pad_len = block_size
    return data + bytes([pad_len] * pad_len)


def _pkcs7_unpad(data: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    if not data or len(data) % block_size != 0:
        raise ValueError("Invalid padded ciphertext length")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size:
        raise ValueError("Invalid PKCS7 padding")
    if data[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Invalid PKCS7 padding")
    return data[:-pad_len]


def _expand_round_keys(key: bytes, rounds: int = NUM_ROUNDS) -> list[bytes]:
    if len(key) != 32:
        raise ValueError("SPN key must be 32 bytes")
    # Simple key schedule: successive hashes of key || round index
    keys: list[bytes] = []
    material = key
    for r in range(rounds):
        material = hashlib.sha256(material + struct.pack("B", r)).digest()
        keys.append(material[:BLOCK_SIZE])
    return keys


def _sub_bytes(block: bytearray, sbox: list[int]) -> None:
    for i in range(BLOCK_SIZE):
        block[i] = sbox[block[i]]


def _permute(block: bytearray, pbox: list[int]) -> None:
    original = bytes(block)
    for i in range(BLOCK_SIZE):
        block[i] = original[pbox[i]]


def _add_round_key(block: bytearray, round_key: bytes) -> None:
    for i in range(BLOCK_SIZE):
        block[i] ^= round_key[i]


def _encrypt_block(block: bytes, round_keys: list[bytes]) -> bytes:
    state = bytearray(block)
    for rk in round_keys:
        _sub_bytes(state, SBOX)
        _permute(state, PBOX)
        _add_round_key(state, rk)
    return bytes(state)


def _decrypt_block(block: bytes, round_keys: list[bytes]) -> bytes:
    state = bytearray(block)
    for rk in reversed(round_keys):
        _add_round_key(state, rk)
        _permute(state, INV_PBOX)
        _sub_bytes(state, INV_SBOX)
    return bytes(state)


def encrypt(plaintext: bytes, key: bytes) -> bytes:
    """Encrypt with custom SPN. Returns version || ciphertext (no salt; salt lives with key)."""
    padded = _pkcs7_pad(plaintext)
    round_keys = _expand_round_keys(key)
    out = bytearray([VERSION])
    for offset in range(0, len(padded), BLOCK_SIZE):
        out.extend(_encrypt_block(padded[offset : offset + BLOCK_SIZE], round_keys))
    return bytes(out)


def decrypt(blob: bytes, key: bytes) -> bytes:
    if len(blob) < 1 + BLOCK_SIZE or (len(blob) - 1) % BLOCK_SIZE != 0:
        raise ValueError("Invalid SPN ciphertext")
    if blob[0] != VERSION:
        raise ValueError("Unsupported SPN ciphertext version")
    round_keys = _expand_round_keys(key)
    plain_padded = bytearray()
    body = blob[1:]
    for offset in range(0, len(body), BLOCK_SIZE):
        plain_padded.extend(_decrypt_block(body[offset : offset + BLOCK_SIZE], round_keys))
    return _pkcs7_unpad(bytes(plain_padded))
