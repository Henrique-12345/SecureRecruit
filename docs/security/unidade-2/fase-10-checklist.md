# Unidade 2 Fase 10 — Hardening mínimo e deploy

## Objetivo

Endurecer o Crypto Lab e preparar deploy (Render API + Vercel frontend) **sem merge ainda**.

## Checklist código

- [x] Endpoints Crypto/Stego/Analytics/Anomalies só `admin`
- [x] `CRYPTO_LAB_ENABLED=false` → 403
- [x] Limites: `CRYPTO_MAX_PLAINTEXT_BYTES`, `STEGO_MAX_COVER_BYTES`, `CRYPTO_LAB_MAX_SEARCHABLE_BITS`
- [x] BF limitado por `CRYPTO_LAB_MAX_ATTACK_ATTEMPTS`
- [x] Auditoria sem plaintext/chave (só tamanhos, fingerprint truncado, métricas)
- [x] Diferencial não persiste hex de plaintext
- [x] Warning se segredos default em `APP_ENV=production`
- [x] Dockerfile cria `/app/uploads/stego`
- [x] Testes `tests/security/test_crypto_hardening.py`
- [ ] Push da branch
- [ ] PR/merge `feature/crypto-lab-unit2` → `main` (depois)
- [ ] Redeploy Render + Vercel

## Variáveis no Render (API)

| Variável | Nota |
|----------|------|
| `DATABASE_URL` | Postgres gerenciado |
| `JWT_SECRET_KEY` | **não** usar `change-me…` |
| `CRYPTO_LAB_ENABLED` | `true` |
| `CRYPTO_MASTER_SECRET` | secreto forte, diferente do JWT |
| `CRYPTO_PBKDF2_ITERATIONS` | `100000` |
| `STEGO_DIRECTORY` | `/app/uploads/stego` |
| `UPLOAD_DIRECTORY` | `/app/uploads` |
| `CORS_ORIGINS` | URL do Vercel |
| `APP_ENV` | `production` |

O `Dockerfile` do backend já roda `alembic upgrade head` + `seed` no boot.

## Vercel (frontend)

1. Root Directory: `frontend`
2. Build: `npm run build`
3. Env: `VITE_API_BASE_URL=https://<sua-api>.onrender.com`
4. Redeploy após o merge

## Smoke pós-deploy

1. Login `admin@example.com` / `Demo@1234`
2. `/admin/crypto` → cifrar → stego → ataque diferencial
3. `/admin/security-dashboard` → gerar carga (opcional) + anomalias
4. Candidato **não** acessa Crypto Lab (403)

## Merge (quando estiver pronto)

```bash
git push
# GitHub → PR feature/crypto-lab-unit2 → main → Merge
# Depois redeploy Render/Vercel
```
