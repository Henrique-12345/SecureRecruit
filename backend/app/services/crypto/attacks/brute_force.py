"""Controlled brute-force against truncated didactic SPN keys (lab only)."""

from __future__ import annotations

import time
from dataclasses import dataclass

from app.services.crypto import custom_cipher


@dataclass
class BruteForceResult:
    found: bool
    attempts: int
    max_attempts: int
    keyspace_size: int
    elapsed_ms: int
    recovered_key_suffix_hex: str | None
    estimated_full_keyspace_years: float
    notes: str


def _with_suffix(full_key: bytes, candidate: int, mask: int) -> bytes:
    """Replace the low searchable bits of the key tail with `candidate`."""
    trial = bytearray(full_key)
    tail = int.from_bytes(bytes(trial[-3:]), "big")
    tail = (tail & ~mask) | (candidate & mask)
    trial[-3:] = tail.to_bytes(3, "big")
    return bytes(trial)


def run_truncated_brute_force(
    *,
    plaintext: bytes,
    ciphertext: bytes,
    full_key: bytes,
    searchable_bits: int,
    max_attempts: int,
) -> BruteForceResult:
    """
    Search only the low `searchable_bits` of the key; remaining bits stay fixed
    from `full_key`. Keeps the demo safe/fast while illustrating BF cost.
    """
    if len(full_key) != 32:
        raise ValueError("Key must be 32 bytes")
    if searchable_bits < 1 or searchable_bits > 24:
        raise ValueError("searchable_bits must be between 1 and 24")

    keyspace = 1 << searchable_bits
    limit = min(max_attempts, keyspace)
    mask = keyspace - 1
    target_suffix = int.from_bytes(full_key[-3:], "big") & mask

    started = time.perf_counter()
    found = False
    attempts = 0
    recovered: str | None = None

    for candidate in range(limit):
        attempts += 1
        trial_key = _with_suffix(full_key, candidate, mask)
        try:
            if custom_cipher.encrypt(plaintext, trial_key) == ciphertext:
                found = True
                recovered = f"{candidate:0{(searchable_bits + 3) // 4}x}"
                break
        except Exception:  # noqa: BLE001
            continue

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    rate = attempts / max(elapsed_ms / 1000.0, 1e-6)
    full_space = 2**256
    years = (full_space / max(rate, 1e-9)) / (3600 * 24 * 365)

    notes = (
        f"Lab BF over {searchable_bits}-bit suffix "
        f"(target={target_suffix}). "
        "Full 256-bit search remains computationally infeasible."
    )
    return BruteForceResult(
        found=found,
        attempts=attempts,
        max_attempts=limit,
        keyspace_size=keyspace,
        elapsed_ms=elapsed_ms,
        recovered_key_suffix_hex=recovered,
        estimated_full_keyspace_years=years,
        notes=notes,
    )


def effectiveness_from_bf(result: BruteForceResult) -> tuple[float, str]:
    """Higher score = more effective attack in the truncated lab setting."""
    if result.found and result.attempts <= result.keyspace_size:
        score = min(1.0, 0.5 + 0.5 * (1 - result.attempts / max(result.keyspace_size, 1)))
        label = "eficaz (chave truncada recuperada no lab)"
    elif result.attempts >= result.keyspace_size and not result.found:
        score = 0.1
        label = "ineficaz no espaço testado"
    else:
        coverage = result.attempts / max(result.keyspace_size, 1)
        score = 0.2 * coverage
        label = "pouco eficaz (espaço não esgotado / não recuperou)"
    return score, label
