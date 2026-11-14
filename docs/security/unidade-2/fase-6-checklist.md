# Unidade 2 Fase 6 — IA / detector de anomalias

## Objetivo

Detectar anomalias com regras + score (e z-score para picos de eventos), distinto da IA de currículo.

## Checklist

- [x] `AnomalyService` — auth_burst, decrypt_fail_rate, file_integrity, access_pattern, event_spike
- [x] Endpoints `/api/v1/anomalies/*` (admin)
- [x] Persistência em `anomaly_events` + auditoria
- [x] Teste: seed de login_failed → `auth_burst`
- [ ] Push da branch

## Endpoints

| Método | Path | Auth |
|--------|------|------|
| POST | `/api/v1/anomalies/run` | admin |
| GET | `/api/v1/anomalies` | admin |
| GET | `/api/v1/anomalies/{id}` | admin |
| PATCH | `/api/v1/anomalies/{id}/resolve` | admin |

## Critérios de aceite

1. ~50 `login_failed` sintéticos → cria `auth_burst`
2. Anomalia listável e resolvível
3. Candidato recebe 403
