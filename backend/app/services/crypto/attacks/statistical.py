"""Statistical ciphertext analysis for the Crypto Lab."""

from __future__ import annotations

from dataclasses import dataclass

from app.services.crypto.metrics import statistical_report


@dataclass
class StatisticalAttackResult:
    report: dict
    notes: str


def run_statistical(ciphertext: bytes) -> StatisticalAttackResult:
    report = statistical_report(ciphertext)
    notes = (
        "Entropia próxima de 8 e χ² próximo da distribuição uniforme "
        "sugerem ciphertext bem misturado (ataque estatístico pouco eficaz)."
    )
    return StatisticalAttackResult(report=report, notes=notes)


def effectiveness_from_statistical(result: StatisticalAttackResult) -> tuple[float, str]:
    entropy = float(result.report.get("entropy_bits", 0.0))
    # Low entropy → more effective statistical distinguishability
    gap = max(0.0, 8.0 - entropy)
    score = min(1.0, gap / 4.0)  # entropy 4 → score 1
    if entropy >= 7.5:
        label = "pouco eficaz (alta entropia / próximo do uniforme)"
    elif entropy >= 6.0:
        label = "moderado (alguma estrutura residual)"
    else:
        label = "eficaz (baixa entropia / padrões exploráveis)"
    return score, label
