# CLAUDE.md - SecureRecruit

## Visão geral

SecureRecruit é uma plataforma web de recrutamento (candidatos, recrutadores, admins) construída como **alvo controlado** do projeto acadêmico **SecureAI Lab** (Cibersegurança Aplicada a Dados e IA, CESAR School). O sistema é funcional de ponta a ponta; o trabalho de segurança (threat model, exploração controlada, correções, reteste, riscos de IA) está documentado por fases em `docs/security/`.

- Todos os dados de demo são fictícios, mas trate dados pessoais (e-mail, currículo, perfil) como sensíveis (LGPD).
- Correções de segurança devem ser reais, não cosméticas; mantenha a documentação das fases coerente com o código.

## Arquitetura e stack

```
Browser → Frontend (React/Vite) → Backend (FastAPI /api/v1) → PostgreSQL
                                        ↓
                             uploads/ (currículos em disco)
                                        ↓
                    AI service (OpenAI se AI_API_KEY, senão heurística local)
```

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL 16, JWT (python-jose, HS256), Argon2id (passlib).
- **Frontend:** React 18, Vite, TypeScript, React Router, Axios.
- **Infra:** Docker Compose (`docker-compose.yml`). Config via `.env` (modelo em `.env.example`).
- **Testes:** pytest (`pytest.ini` na raiz, `pythonpath = backend`).
- Docs de referência: `README.md`, `docs/architecture/architecture.md`, `docs/api/api.md`.

## Mapa de diretórios

### `backend/app`
| Pasta | Conteúdo |
|-------|----------|
| `main.py` | App FastAPI, CORS, handlers de erro, inclusão do router |
| `api/v1/` | Routers: `auth`, `users`, `candidates`, `recruiters`, `resumes`, `jobs`, `applications`, `ai`, `admin`, `logs` |
| `core/` | `config` (settings), `database` (engine/`get_db`), `security` (hash + JWT), `enums` (`UserRole`, `SecurityEventType`…), `exceptions` |
| `dependencies/auth.py` | `get_current_user`, `require_roles` e aliases `CurrentUser`, `CandidateUser`, `RecruiterUser`, `AdminUser`, `DbSession` |
| `models/` | Entidades SQLAlchemy: User, CandidateProfile, Resume, Job, Application, AIAnalysis, SecurityLog |
| `schemas/` | Schemas Pydantic de entrada/saída |
| `services/` | Regras de negócio e ownership: `auth`, `job`, `application`, `resume` (upload), `ai`, `audit`, `hash` |
| `scripts/seed.py` | Seed de usuários/dados de demo |
| `utils/` | `masking` (mascarar e-mails), `request` (IP / user-agent) |

Migrations em `backend/alembic/versions/`.

### `frontend/src`
| Pasta | Conteúdo |
|-------|----------|
| `api/client.ts` | Instância Axios com Bearer token |
| `auth/` | `AuthContext`, `ProtectedRoute` |
| `components/` | `AppLayout` (menus por papel) |
| `pages/` | Login, Register, Jobs, JobDetail + `admin/`, `candidate/`, `recruiter/` |
| `types.ts` | Tipos compartilhados |

### Outros
- `tests/functional/`, `tests/security/` - testes pytest; `tests/conftest.py` cria o DB `securerecruit_test` e usa rollback por teste.
- `docs/security/` - fases 0–4 (checklists, threat model/matriz de riscos, exploração, correções/reteste, segurança de IA) e `evidence/` com screenshots.
- `uploads/` - armazenamento local de currículos (não versionar conteúdo real).

## Autenticação e autorização

- Senhas com Argon2id; login gera JWT HS256 com claims `sub` (user id) e `role`. Logout apenas registra evento (JWT stateless).
- `get_current_user` valida o token, carrega o usuário e bloqueia contas inativas.
- Papel: use os aliases de `dependencies/auth.py` (`CandidateUser`, `RecruiterUser` = recruiter+admin, `AdminUser`) ou `require_roles(...)`. Negações são auditadas.
- **Ownership** (ex.: recrutador só gerencia suas vagas; candidato só vê seus currículos/candidaturas) é verificado nos **services**, não só na rota.
- **O frontend NÃO é fronteira de segurança.** Ele só esconde menus/rotas. Toda regra de acesso precisa existir e ser testada no backend.
- Todo endpoint novo deve começar restritivo (least privilege) e ter teste de autorização em `tests/security/`.

## Comandos

```bash
cp .env.example .env
docker compose up --build        # frontend :5173, API :8000/docs, Postgres :5432
```

Backend (local):
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.scripts.seed
uvicorn app.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend
npm install
npm run dev        # dev server
npm run build      # tsc --noEmit + vite build
```

Testes (a partir da **raiz**, com a venv do backend ativa e PostgreSQL acessível via `DATABASE_URL`):
```bash
pytest -q
pytest tests/security -q
```

Usuários demo (senha `Demo@1234`): `admin@example.com`, `ana.recruiter@example.com`, `bruno.recruiter@example.com`, `carlos.candidate@example.com`, `diana.candidate@example.com`, `eduardo.candidate@example.com`.

## Convenções

- **Sempre ORM** (SQLAlchemy). Não concatenar SQL; `text()` só com parâmetros bindados e quando inevitável.
- **Validação com Pydantic** em `schemas/` para toda entrada e saída; não retornar models crus nem campos sensíveis (ex.: `password_hash`).
- Rotas finas: lógica de negócio e checagens de ownership ficam em `services/`.
- **Eventos de segurança via `AuditService.log_event`** (login, falhas, acesso negado, upload, IA, ações admin). Nunca logar senhas, tokens ou conteúdo de currículo; e-mails são mascarados.
- Erros via exceções de `core/exceptions.py`, retornando `{"detail": "..."}` sem stack trace.
- Uploads: respeitar `MAX_UPLOAD_SIZE` e `ALLOWED_FILE_TYPES`; integridade por SHA-256 (`hash_service`).
- **Texto de currículo é dado não confiável.** Em `ai_service.py`, mantenha instruções de sistema separadas do bloco `UNTRUSTED RESUME DATA`, passe pelo sanitizador de prompt injection e valide a saída com `AIAnalysisResult` antes de persistir.
- Segredos só via `.env`/settings; nunca hardcode.
- Ao corrigir vulnerabilidade, adicionar teste de regressão e atualizar a fase correspondente em `docs/security/`.

## Git

Commits e push são feitos **manualmente pelo humano**. Não executar `git commit`, `git push` ou comandos que alterem o histórico; apenas deixar as alterações no working tree.
