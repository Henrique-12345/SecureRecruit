# Unidade 2 Fase 4 — Ataques controlados + métricas

## Objetivo

Executar BF (chave truncada), diferencial e estatístico **somente** contra a cifra didática SPN, com limites de lab.

## Checklist

- [x] `attacks/brute_force.py` — espaço truncado (≤20 bits) + extrapolação 256-bit
- [x] `attacks/differential.py` — avalanche / Hamming
- [x] `attacks/statistical.py` — entropia / χ²
- [x] `attack_lab_service.py` — persiste `AttackExperiment` + `CryptoOperation`
- [x] Endpoints `/api/v1/crypto/attacks/*`
- [x] Conclusão automática (`result_summary` / `effectiveness_score`)
- [x] Testes `tests/security/test_crypto_attacks.py`
- [ ] Push da branch

## Endpoints

| Método | Path | Auth |
|--------|------|------|
| POST | `/api/v1/crypto/attacks/brute-force` | admin |
| POST | `/api/v1/crypto/attacks/differential` | admin |
| POST | `/api/v1/crypto/attacks/statistical` | admin |
| GET | `/api/v1/crypto/attacks/experiments` | admin |
| GET | `/api/v1/crypto/attacks/experiments/{id}` | admin |

## Critérios de aceite

1. Três ataques executáveis com métricas numéricas
2. Label automática (eficaz / pouco eficaz / …)
3. AES **não** é alvo do BF de lab (apenas SPN)
4. Candidato recebe 403
