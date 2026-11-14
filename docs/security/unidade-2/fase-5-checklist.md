# Unidade 2 Fase 5 — Big Data de eventos / analytics

## Objetivo

Agregar volume experimental (crypto + auth + attacks) para o dashboard e demos.

## Checklist

- [x] `analytics_service.py` — summary, timeseries, auth/crypto failures, seed-load
- [x] Router `/api/v1/analytics/*` (admin)
- [x] Script `python -m app.scripts.seed_crypto_lab`
- [x] Testes `tests/security/test_analytics.py`
- [ ] Push da branch

## Endpoints

| Método | Path | Auth |
|--------|------|------|
| GET | `/api/v1/analytics/events/summary` | admin |
| GET | `/api/v1/analytics/events/timeseries` | admin |
| GET | `/api/v1/analytics/auth/failures` | admin |
| GET | `/api/v1/analytics/crypto/failures` | admin |
| POST | `/api/v1/analytics/seed-load` | admin |

## Seed CLI

```bash
cd backend
python -m app.scripts.seed_crypto_lab --crypto 5000 --auth 500 --attacks 100
```

## Critérios de aceite

1. Seed ≥ 1k eventos sem erro
2. Summary/timeseries retornam contagens coerentes
3. Candidato recebe 403
