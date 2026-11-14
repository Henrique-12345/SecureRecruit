"""Differential analysis helper for the didactic SPN (lab)."""

from __future__ import annotations

from dataclasses import dataclass

from app.services.crypto import custom_cipher
from app.services.crypto.metrics import avalanche_score, hamming_distance


@dataclass
class DifferentialResult:
    plaintext_len: int
    ciphertext_a_len: int
    ciphertext_b_len: int
    hamming_bits: int
    avalanche_score: float
    flipped_input_bits: int
    notes: str


def run_differential(
    *,
    plaintext: bytes,
    key: bytes,
    flip_byte_index: int = 0,
    flip_bit_mask: int = 0x01,
) -> DifferentialResult:
    if not plaintext:
        raise ValueError("plaintext required")
    idx = max(0, min(flip_byte_index, len(plaintext) - 1))
    mutated = bytearray(plaintext)
    mutated[idx] ^= flip_bit_mask & 0xFF

    c1 = custom_cipher.encrypt(plaintext, key)
    c2 = custom_cipher.encrypt(bytes(mutated), key)
    score = avalanche_score(c1, c2)
    ham = hamming_distance(c1, c2)
    flipped_in = bin(flip_bit_mask & 0xFF).count("1")

    notes = (
        "Avalanche próximo de 0.5 indica boa difusão (ataque diferencial menos revelador). "
        "Valores baixos sugerem difusão fraca. Plaintext nunca é persistido."
    )
    return DifferentialResult(
        plaintext_len=len(plaintext),
        ciphertext_a_len=len(c1),
        ciphertext_b_len=len(c2),
        hamming_bits=ham,
        avalanche_score=score,
        flipped_input_bits=flipped_in,
        notes=notes,
    )


def effectiveness_from_differential(result: DifferentialResult) -> tuple[float, str]:
    """Attack 'effectiveness' as how much weak diffusion is exposed (far from 0.5)."""
    distance = abs(result.avalanche_score - 0.5)
    # Cap: distance 0.5 → score 1.0 (very weak diffusion)
    score = min(1.0, distance * 2.0)
    if result.avalanche_score >= 0.4:
        label = "pouco eficaz (boa difusão observada ≈0.5)"
    elif result.avalanche_score >= 0.25:
        label = "moderadamente revelador (difusão parcial)"
    else:
        label = "eficaz em expor difusão fraca"
    return score, label
