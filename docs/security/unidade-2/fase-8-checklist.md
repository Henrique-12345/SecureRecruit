# Unidade 2 Fase 8 — Integração, seed, testes e evidências

## Objetivo

Fechar o laboratório com volume de dados, suite de regressão e pasta de evidências pronta para prints.

## Checklist

### Seed
- [x] PNG de capa demo (`uploads/stego/cover_demo.png` via seed)
- [x] Script `python -m app.scripts.seed_crypto_lab` (defaults ≥ 8k crypto)
- [x] Flag `--run-anomalies` para gerar `auth_burst`
- [x] Gerador de artefatos JSON: `python -m app.scripts.generate_lab_evidence`

### Testes automatizados
- [x] Round-trip SPN / AES — `tests/security/test_crypto_lab.py`
- [x] Chaves diferentes → ciphertext diferente
- [x] Stego embed/extract — `tests/security/test_stego_lab.py`
- [x] Differential + BF + statistical — `tests/security/test_crypto_attacks.py`
- [x] Candidate 403 em `/crypto/*`
- [x] Anomaly `auth_burst` — `tests/security/test_anomaly_detection.py`
- [x] Analytics seed — `tests/security/test_analytics.py`

### Evidências
- [x] Estrutura `docs/security/evidence/unidade-2/{00..06,artifacts}/`
- [x] Artefatos JSON/PNG gerados em `artifacts/`
- [ ] Prints da UI (equipe) nas pastas 01–06
- [ ] Push da branch

## Comandos

```bash
# Postgres
docker compose up -d postgres

# Seed demo users (se ainda não rodou)
cd backend
DATABASE_URL='postgresql+psycopg://securerecruit:securerecruit@localhost:5433/securerecruit' \
  PYTHONPATH=. python -m app.scripts.seed

# Volume + anomalias
DATABASE_URL='postgresql+psycopg://securerecruit:securerecruit@localhost:5433/securerecruit' \
  STEGO_DIRECTORY=/home/fatima/Henrique_projetos/SecureRecruit/uploads/stego \
  PYTHONPATH=. python -m app.scripts.seed_crypto_lab --crypto 8000 --auth 400 --attacks 120 --run-anomalies

# Artefatos de evidência (sem UI)
DATABASE_URL='postgresql+psycopg://securerecruit:securerecruit@localhost:5433/securerecruit' \
  PYTHONPATH=. python -m app.scripts.generate_lab_evidence

# Testes Unidade 2
cd ..
DATABASE_URL='postgresql+psycopg://securerecruit:securerecruit@localhost:5433/securerecruit' \
  PYTHONPATH=backend python -m pytest tests/security/test_crypto_lab.py \
  tests/security/test_stego_lab.py tests/security/test_crypto_attacks.py \
  tests/security/test_analytics.py tests/security/test_anomaly_detection.py -q
```

## Critério de conclusão

1. Seed ≥ ~1k–8k eventos sem erro
2. Suite acima verde
3. Pasta de evidências pronta (JSON gerados; prints UI pela equipe)
