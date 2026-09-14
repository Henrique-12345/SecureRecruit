# API — SecureRecruit

Base: `/api/v1`

Documentação interativa: `GET /docs` (Swagger) e `GET /redoc`.

## Auth

| Método | Path | Auth | Descrição |
|--------|------|------|-----------|
| POST | `/auth/register` | pública | Cadastro (candidate/recruiter) |
| POST | `/auth/login` | pública | Login email+senha → JWT |
| GET | `/auth/me` | JWT | Usuário atual |
| POST | `/auth/logout` | JWT | Registra logout (JWT stateless) |

## Users / Candidates / Recruiters

| Método | Path | Descrição |
|--------|------|-----------|
| GET/PUT | `/users/me` | Dados básicos do usuário |
| GET/PUT | `/candidates/me` | Perfil profissional do candidato |
| GET | `/candidates/{id}` | Perfil público autorizado |
| GET | `/recruiters/me/jobs` | Vagas do recrutador |

## Resumes

| Método | Path | Descrição |
|--------|------|-----------|
| POST | `/resumes` | Upload multipart |
| GET | `/resumes` | Lista autorizada |
| GET | `/resumes/{id}` | Metadados |
| GET | `/resumes/{id}/download` | Download do arquivo |
| DELETE | `/resumes/{id}` | Exclusão |
| GET | `/resumes/{id}/integrity` | Verificação SHA-256 (admin) |

## Jobs / Applications

| Método | Path | Descrição |
|--------|------|-----------|
| GET | `/jobs` | Lista (candidatos: abertas; `mine=true` para recrutador) |
| POST/PUT/DELETE | `/jobs` / `/jobs/{id}` | Gestão de vagas |
| POST | `/jobs/{id}/applications` | Candidatura |
| GET | `/applications/me` | Candidaturas do candidato |
| GET | `/jobs/{id}/applications` | Candidaturas da vaga |
| PATCH | `/applications/{id}/status` | Alteração de status |

## AI / Admin / Logs

| Método | Path | Descrição |
|--------|------|-----------|
| POST | `/ai/analyze-resume` | Análise de currículo |
| POST | `/ai/match-resume-job` | Match currículo×vaga |
| GET | `/ai/analyses/{id}` | Consulta análise |
| GET | `/admin/users` | Lista usuários |
| PATCH | `/admin/users/{id}/status` | Ativar/desativar |
| GET | `/admin/logs` | Logs de segurança |
| GET | `/admin/applications` | Todas candidaturas |
| GET | `/logs` | Alias admin de logs |

## Códigos HTTP

200, 201, 204, 400, 401, 403, 404, 409, 422, 500 — com corpo JSON `{ "detail": "..." }` sem stack traces.
