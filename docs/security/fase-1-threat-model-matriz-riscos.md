# Fase 1 - Threat Modeling e Matriz de Riscos

**Projeto:** SecureRecruit (SecureAI Lab)  
**Disciplina:** Cibersegurança Aplicada a Dados e IA  
**Ambiente analisado:** produção acadêmica (Vercel + Render + PostgreSQL)  
**Data-base da análise:** versão na branch `security-analysis` / app publicada  

Este documento atende à etapa de análise de segurança **antes** dos testes de exploração.

---

## 1. Contextualização rápida

A SecureRecruit é uma plataforma web de recrutamento e seleção com:

- Frontend React (Vercel) - `https://secure-recruit.vercel.app`
- API FastAPI (Render) - `https://securerecruit-api.onrender.com`
- Banco PostgreSQL (Render)
- Upload de currículos, análise por IA e logs de auditoria

**Público-alvo:** candidatos, recrutadores e administradores (dados fictícios para fins acadêmicos).

---

## 2. Ativos

| ID | Ativo | Descrição | Criticidade |
|----|-------|-----------|-------------|
| A1 | API REST (`/api/v1`) | Endpoints de negócio e administração | Alta |
| A2 | Banco PostgreSQL | Usuários, perfis, vagas, candidaturas, hashes, logs | Alta |
| A3 | Arquivos de currículo | PDF/DOCX em storage do backend | Alta |
| A4 | Segredos de configuração | `JWT_SECRET_KEY`, `DATABASE_URL`, etc. | Alta |
| A5 | Tokens JWT | Sessão lógica do usuário autenticado | Alta |
| A6 | Serviço / fluxo de IA | Análise e match currículo×vaga | Média |
| A7 | Frontend | Interface e armazenamento local do token | Média |
| A8 | Logs de segurança | Trilha de auditoria | Média |
| A9 | Contas de usuário | Credenciais (hash) e papéis | Alta |

---

## 3. Dados tratados

| Dado | Exemplos | Classificação (acadêmica) | Onde aparece |
|------|----------|--------------------------|--------------|
| Identificação | nome, email | Pessoal | `users`, APIs, UI |
| Documento | CPF fictício | Pessoal sensível (simulado) | `users` |
| Contato | telefone | Pessoal | `users` |
| Perfil profissional | skills, experiência, endereço | Pessoal / profissional | `candidate_profiles` |
| Currículo | arquivo + metadados + SHA-256 | Pessoal / arquivo | `resumes`, storage |
| Autenticação | `password_hash`, JWT | Credencial / segredo de sessão | DB / cliente |
| Operacional | vagas, candidaturas, status | Negócio | `jobs`, `applications` |
| IA | texto de análise, score, skills extraídas | Derivado | `ai_analyses` |
| Auditoria | IP, user-agent, ação, sucesso | Operacional / segurança | `security_logs` |

**Observação LGPD (acadêmica):** os dados de demonstração são **fictícios**, mas o sistema é modelado como se tratasse dados pessoais reais.

---

## 4. Usuários e privilégios

| Papel | Pode | Não pode (esperado) |
|-------|------|---------------------|
| Anônimo | Ver vagas abertas (leitura pública limitada) | Ações autenticadas |
| `candidate` | Perfil próprio, upload/CV próprio, candidaturas próprias, IA sobre próprios dados | Admin, logs, vagas de terceiros, CVs alheios |
| `recruiter` | CRUD das próprias vagas, candidaturas/CVs ligados às suas vagas, IA nesses contextos | Admin de usuários/logs, alterar outros recrutadores |
| `admin` | Usuários, status de contas, logs, visão ampla, checagem de integridade | (Poder amplo - risco de abuso de privilégio) |

**Controle de UI ≠ segurança:** o frontend esconde menus; a autorização efetiva deve estar no backend.

---

## 5. Superfícies de ataque

```text
[Navegador / Atacante]
        |  HTTPS
        v
[Frontend Vercel] --JWT em localStorage--> [API Render /api/v1]
                                                |
                        +-----------------------+-----------------------+
                        v                       v                       v
                 [PostgreSQL]            [uploads/ arquivos]      [Serviço de IA]
                        |
                 [security_logs]
```

Superfícies principais:

1. Autenticação (`/auth/login`, `/auth/register`, JWT)
2. Autorização por ID de recurso (resumes, applications, candidates, jobs)
3. Upload/download de arquivos
4. Endpoints administrativos
5. Entrada de texto não confiável para IA (conteúdo do currículo)
6. Configuração (CORS, secrets, DEBUG, storage efêmero)
7. Frontend (XSS armazenado/refletido via campos de texto)
8. Integridade de arquivos (hash vs conteúdo em disco)

---

## 6. Ameaças (STRIDE resumido)

| Ameaça | Exemplos na SecureRecruit |
|--------|---------------------------|
| Spoofing | Uso de token JWT roubado; impersonação de papel |
| Tampering | Alteração de arquivo de currículo no storage; manipulação de score via prompt injection |
| Repudiation | Ações sem log adequado (mitigado parcialmente por `security_logs`) |
| Information Disclosure | IDOR lendo CV/PII de outro usuário; vazamento em logs/erros |
| Denial of Service | Upload grande/repetido; abuse da IA |
| Elevation of Privilege | Candidate acessando `/admin/*`; privilege confusion no JWT `role` |

---

## 7. Vulnerabilidades potenciais (hipóteses para teste)

| ID | Hipótese | Categoria do edital |
|----|----------|---------------------|
| V1 | Falha de autorização / IDOR em recursos por UUID | Autorização / Broken Access Control / API |
| V2 | Validação incompleta de upload (MIME/extensão/conteúdo) | Upload inseguro |
| V3 | Prompt injection via texto do currículo | Vulnerabilidades de IA |
| V4 | Adulteração de arquivo sem detecção contínua | Integridade |
| V5 | Exposição excessiva de PII em respostas/logs | Exposição indevida de dados |
| V6 | XSS em campos ricos (summary, description) | XSS |
| V7 | Configuração fraca (CORS amplo, DEBUG, segredo previsível) | Configuração |
| V8 | Sessão JWT sem revogação real no logout | Gerenciamento de sessão |

**Seleção para exploração na Fase 2 (prioritária):** **V1, V2, V3** (e V4 como bônus de integridade).

---

## 8. Controles de segurança já existentes (baseline)

- Senhas com Argon2id (sem plaintext no banco)
- JWT + autorização por papel no backend
- Validação Pydantic / ORM
- Upload com limite de tamanho, MIME e extensão; nome interno aleatório
- SHA-256 e endpoint admin de integridade
- Logs de eventos de segurança
- HTTPS em produção (Vercel/Render)
- Secrets via variáveis de ambiente
- Delimitação de prompt (system vs “UNTRUSTED RESUME DATA”)
- Utilitários de mascaramento (CPF/email/telefone)

---

## 9. Matriz de Riscos

Escala:

- **P** Probabilidade: 1 (baixa) – 3 (alta)
- **I** Impacto: 1 (baixo) – 3 (alto)
- **R** Risco = P × I (1–3 baixo; 4–6 médio; 7–9 alto)

| ID | Ameaça / cenário | Ativo | P | I | R | Nível | Controle atual | Lacuna / teste |
|----|------------------|-------|---|---|---|-------|----------------|----------------|
| R1 | IDOR: usuário acessa currículo/candidatura/candidato de outro | A1, A2, A3 | 2 | 3 | 6 | Médio | Checagens de ownership em serviços | Validar todos os GETs/downloads na Fase 2 |
| R2 | Upload malicioso ou bypass de tipo | A3, A1 | 2 | 3 | 6 | Médio | MIME, extensão, size, nome UUID | Testar inconsistência MIME×conteúdo |
| R3 | Prompt injection altera análise/score | A6 | 3 | 2 | 6 | Médio | Separação system/dados + schema | Demonstrar influência do texto do CV |
| R4 | Arquivo adulterado no disco | A3 | 2 | 3 | 6 | Médio | SHA-256 + check admin | Verificar se há checagem antes de IA/download |
| R5 | Vazamento de PII em API/logs | A2, A8 | 2 | 2 | 4 | Médio | Authz + masking utilitário | Revisar payloads e logs |
| R6 | Roubo de JWT (XSS/localStorage) | A5, A7 | 2 | 3 | 6 | Médio | HTTPS; logout só audita | Sem denylist de token; XSS potencial |
| R7 | Abuso de conta admin | A9, A2 | 1 | 3 | 3 | Baixo | Poucos admins; logs | MFA não implementado (justificar no relatório) |
| R8 | Config/CORS/secrets inadequados | A4, A1 | 2 | 2 | 4 | Médio | Env vars; CORS configurável | Revisar valores de produção |
| R9 | Indisponibilidade (cold start / free tier) | A1 | 3 | 1 | 3 | Baixo | Healthcheck | Limitação de infra, não bug de app |

---

## 10. Controles necessários (alvo pós-análise)

| Prioridade | Controle | Relacionado a |
|------------|----------|---------------|
| Alta | Garantir autorização consistente em todos os recursos por ID | R1 |
| Alta | Endurecer validação de upload (conteúdo/magic bytes) | R2 |
| Alta | Mitigar prompt injection (sanitização/política de saída) | R3 |
| Média | Verificar integridade antes de uso sensível do arquivo | R4 |
| Média | Minimizar PII em respostas e aplicar máscaras em logs | R5 |
| Média | Revisar armazenamento de token / headers de segurança | R6 |
| Baixa | Documentar ausência de MFA e plano futuro | R7 |

---

## 11. Diagrama textual de fluxo de risco (IA)

```text
Currículo (dado NÃO CONFIÁVEL)
        |
        v
Extração de texto → Prompt (system + delimitadores + job)
        |
        v
Modelo IA / heurística local → AIAnalysis (score, skills, texto)
        |
        v
Risco: instruções embutidas no CV influenciam score/resumo
Mitigação-alvo: validação de saída + política anti-instrução + reteste
```

---

## 12. Conclusão da Fase 1

A SecureRecruit possui baseline razoável (authn/authz, hash, HTTPS, logs, IA delimitada), mas apresenta superfícies claras para estudo acadêmico. Os riscos **R1–R3** (e R4 como integridade) são os mais adequados para a sequência:

**Fase 2 Exploração → Fase 3 Correção/Reteste → Fase 4 IA.**

---

## Evidências associadas (Fase 0)

Já coletadas em `evidence/00-ambiente/`:

- `frontend_app.png`
- `backend_health.png`
- `backend_swagger.png`
- `dashboard_candidato.png`
- `dashboard_recrutador.png`
- `dashboard_admin.png`
- `tabela_usuarios.png`
