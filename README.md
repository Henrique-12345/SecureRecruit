# SecureRecruit

Plataforma web de recrutamento e seleção desenvolvida como **alvo controlado** para um projeto acadêmico de **Cibersegurança Aplicada a Dados e IA**.

Esta versão entrega o sistema **funcional completo** (frontend + backend + PostgreSQL + autenticação + autorização + upload + IA + logs). Análise ofensiva, exploração e correção de vulnerabilidades ficam para etapas posteriores.

## 1. Objetivo

Permitir que candidatos, recrutadores e administradores utilizem um fluxo realista de recrutamento, com superfícies técnicas suficientes para futura análise de segurança acadêmica.

## 2. Arquitetura

```
Browser → Frontend (React/Vite) → Backend (FastAPI /api/v1) → PostgreSQL
                                         ↓
                                      uploads/
                                         ↓
                                      AI service (OpenAI opcional / heurística local)
```

## 3. Tecnologias

- **Backend:** Python 3.12, FastAPI, SQLAlchemy, Alembic, PostgreSQL, JWT, Argon2id
- **Frontend:** React, Vite, TypeScript, React Router, Axios
- **Infra:** Docker Compose
- **Testes:** pytest

## 4. Como instalar

```bash
cp .env.example .env
```

### Com Docker (recomendado)

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend/API docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432

### Desenvolvimento local

**Pré-requisitos:** Python 3.12+, Node.js 20+, PostgreSQL 16.

```bash
# Banco
# Crie o database `securerecruit` e ajuste DATABASE_URL no .env

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.scripts.seed
uvicorn app.main:app --reload --port 8000

# Frontend (outro terminal)
cd frontend
npm install
npm run dev
```

## 5–6. Variáveis de ambiente

Veja `.env.example`:

| Variável | Descrição |
|----------|-----------|
| `DATABASE_URL` | URL SQLAlchemy do PostgreSQL |
| `JWT_SECRET_KEY` | Segredo do JWT |
| `JWT_ALGORITHM` | Algoritmo (HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do token |
| `AI_API_KEY` | Chave OpenAI (opcional) |
| `UPLOAD_DIRECTORY` | Diretório de currículos |
| `MAX_UPLOAD_SIZE` | Limite em bytes |
| `ALLOWED_FILE_TYPES` | MIME types aceitos |
| `CORS_ORIGINS` | Origens permitidas |

Sem `AI_API_KEY`, o sistema usa analisador heurístico local determinístico.

## 7. Migrations

```bash
cd backend
alembic upgrade head
```

## 8. Seed

```bash
cd backend
python -m app.scripts.seed
```

## 9–10. Frontend e Backend

Já descritos acima. A API Swagger fica em `/docs`.

## 11. Usuários de demonstração (fictícios)

Senha de todos: `Demo@1234`

| Papel | Email |
|-------|-------|
| Admin | `admin@example.com` |
| Recrutadora | `ana.recruiter@example.com` |
| Recrutador | `bruno.recruiter@example.com` |
| Candidato | `carlos.candidate@example.com` |
| Candidata | `diana.candidate@example.com` |
| Candidato | `eduardo.candidate@example.com` |

## 12. Principais endpoints

- `POST /api/v1/auth/register|login` · `GET /api/v1/auth/me` · `POST /api/v1/auth/logout`
- `GET|PUT /api/v1/users/me`
- `GET|PUT /api/v1/candidates/me`
- `POST|GET|DELETE /api/v1/resumes` · `GET /api/v1/resumes/{id}/download`
- `GET|POST|PUT|DELETE /api/v1/jobs`
- `POST /api/v1/jobs/{id}/applications` · `PATCH /api/v1/applications/{id}/status`
- `POST /api/v1/ai/analyze-resume` · `POST /api/v1/ai/match-resume-job`
- `GET /api/v1/admin/users` · `GET /api/v1/admin/logs`

Documentação detalhada: `docs/api/api.md`.

## 13. Arquitetura da IA

Serviço centralizado em `backend/app/services/ai_service.py`:

1. Extrai texto do currículo (PDF/DOCX)
2. Monta prompt com **instruções de sistema** separadas do bloco **UNTRUSTED RESUME DATA**
3. Chama OpenAI se houver chave; caso contrário, usa heurística local
4. Valida saída com Pydantic (`AIAnalysisResult`)
5. Persiste em `ai_analyses` e registra log de auditoria

## Testes

```bash
cd backend && source .venv/bin/activate
cd ..
pytest -q
```

## Documentação adicional

- `docs/architecture/architecture.md`
- `docs/api/api.md`
- `docs/security/security-baseline.md`
