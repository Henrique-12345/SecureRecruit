# Arquitetura — SecureRecruit

## Visão geral

Monorepo com frontend React, backend FastAPI e PostgreSQL orquestrados por Docker Compose.

## Componentes

| Componente | Responsabilidade |
|------------|------------------|
| `frontend/` | UI, estado de autenticação JWT, rotas por papel |
| `backend/app/api` | Endpoints REST versionados em `/api/v1` |
| `backend/app/services` | Regras de negócio, upload, IA, auditoria, hash |
| `backend/app/models` | Entidades SQLAlchemy |
| `backend/app/dependencies` | Autenticação e autorização |
| `uploads/` | Armazenamento de currículos em disco |
| `tests/` | Testes funcionais e baseline de autorização |

## Modelo de dados (resumo)

- User 1—1 CandidateProfile
- User(candidate) 1—N Resume
- User(recruiter) 1—N Job
- Application N—1 Candidate, Job, Resume
- AIAnalysis N—1 Resume, 0..1 Job
- SecurityLog 0..1 User

## Autenticação e autorização

- Senhas com Argon2id
- JWT Bearer com claims `sub` e `role`
- Dependencies `require_roles` no backend
- Frontend apenas esconde menus (não é controle de segurança)

## IA

Prompt com delimitadores explícitos entre instruções do sistema e dados não confiáveis do currículo, permitindo futura demonstração de prompt injection sem misturar responsabilidades no código.
