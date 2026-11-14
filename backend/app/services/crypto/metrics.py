"""Cryptographic metrics for lab demonstrations (avalanche, entropy, histogram)."""

from __future__ import annotations

import math
from collections import Counter


def hamming_distance(a: bytes, b: bytes) -> int:
    n = min(len(a), len(b))
    dist = 0
    for i in range(n):
        x = a[i] ^ b[i]
        dist += x.bit_count()
    dist += 8 * abs(len(a) - len(b))
    return dist


def avalanche_score(cipher_a: bytes, cipher_b: bytes) -> float:
    """Fraction of bits that differ (0–1). Ideal ~0.5 for strong diffusion."""
    total_bits = max(len(cipher_a), len(cipher_b)) * 8
    if total_bits == 0:
        return 0.0
    return hamming_distance(cipher_a, cipher_b) / total_bits


def byte_histogram(data: bytes) -> dict[str, int]:
    counts = Counter(data)
    return {f"{b:02x}": counts.get(b, 0) for b in range(256)}


def shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    length = len(data)
    entropy = 0.0
    for count in counts.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy


def statistical_report(data: bytes) -> dict:
    hist = Counter(data)
    length = max(len(data), 1)
    # Chi-square vs uniform over 256 bins
    expected = length / 256.0
    chi2 = 0.0
    for b in range(256):
        observed = hist.get(b, 0)
        chi2 += (observed - expected) ** 2 / expected if expected else 0.0
    return {
        "length": len(data),
        "entropy_bits": round(shannon_entropy(data), 6),
        "max_entropy_bits": 8.0,
        "chi_square_uniform": round(chi2, 4),
        "unique_bytes": len(hist),
        # Compact top frequencies for UI (not full 256 map)
        "top_bytes": [
            {"byte": f"{b:02x}", "count": c, "ratio": round(c / length, 6)}
            for b, c in hist.most_common(16)
        ],
    }
