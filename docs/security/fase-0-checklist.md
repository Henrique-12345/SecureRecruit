# Checklist — Fase 0 (Preparação)

Marque com `[x]` quando concluir.

## Ambiente

- [ ] `GET /health` retorna OK
- [ ] Swagger `/docs` abre
- [ ] Frontend Vercel abre
- [ ] Login **candidate** OK
- [ ] Login **recruiter** OK
- [ ] Login **admin** OK

## URLs oficiais (anotar no relatório)

- [ ] Frontend: `https://secure-recruit.vercel.app`
- [ ] Backend: `https://securerecruit-api.onrender.com`
- [ ] Swagger: `https://securerecruit-api.onrender.com/docs`
- [ ] GitHub: `https://github.com/Henrique-12345/SecureRecruit`

## Repositório

- [ ] Branch `security-analysis` criada
- [ ] Pasta `docs/security/evidence/` criada
- [ ] Prints iniciais salvos em `evidence/00-ambiente/`

## Prints esperados em `evidence/00-ambiente/`

- [ ] `health-ok.png`
- [ ] `swagger-ok.png` (opcional, mas recomendado)
- [ ] `frontend-home.png` (opcional)
- [ ] `login-candidate.png` (dashboard do candidato)
- [ ] `login-recruiter.png` (dashboard do recrutador)
- [ ] `login-admin.png` (dashboard do admin)
- [ ] `db-users.png` (opcional — DBeaver com emails/roles)

## Critério de conclusão

Fase 0 concluída quando ambiente validado, branch ativa e prints dos 3 dashboards estiverem em `00-ambiente/`.
