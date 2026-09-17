# Fase 2b - Exploração controlada (R5: exposição de PII)

**Formato:** Vulnerabilidade → Método → Evidência → Impacto

**Categoria do edital:** exposição indevida de dados / LGPD (minimização)
**Risco da matriz:** R5 - Vazamento de PII em API/logs (P=2, I=2, Médio) - ver `fase-1-threat-model-matriz-riscos.md`
**Ambiente:** SecureRecruit (Swagger `/docs`), contas demo (`Demo@1234`)

> Teste controlado na própria aplicação da equipe, para o SecureAI Lab.

---

## Vulnerabilidade

As respostas administrativas de usuário retornam **CPF, telefone e data de nascimento em claro** de **todos** os usuários da plataforma.

- `backend/app/schemas/user.py`: `UserAdminRead` herdava de `UserRead` → `UserBase`, que inclui `cpf`, `phone` e `birth_date` sem tratamento.
- `backend/app/api/v1/admin.py`: `GET /admin/users`, `GET /admin/users/{id}` (e `PATCH /admin/users/{id}/status`) serializavam o model direto nesse schema.
- O utilitário `backend/app/utils/masking.py` (`mask_cpf`, `mask_phone`, `mask_email`, `mask_name`) existia, mas **não era aplicado em nenhuma resposta da API**: controle de segurança construído e não usado.

Fora do escopo (comportamento correto, não alterado):
- `GET /candidates/{id}` já usa `CandidatePublicRead` (sem CPF).
- `GET /users/me`, `GET /auth/me`, `GET /recruiters/me` retornam os dados **do próprio usuário**; o titular ver o próprio dado é legítimo (LGPD art. 18, II - acesso aos dados).

---

## Método

1. Abrir o Swagger (`/docs`).
2. `POST /api/v1/auth/login` com `admin@example.com` / `Demo@1234`; copiar o `access_token`.
3. **Authorize** → `Bearer <token>`.
4. `GET /api/v1/admin/users` → **Execute**.
5. Observar no corpo da resposta os campos `cpf`, `phone` e `birth_date` de cada usuário.
6. (Opcional) `GET /api/v1/admin/users/{id}` para um candidato → mesmos campos em claro.

**Resultado observado (antes da correção):**

```json
{
  "name": "Candidato Carlos Mendes",
  "email": "carlos.candidate@example.com",
  "cpf": "333.333.333-33",
  "phone": "(81) 93333-3333",
  "birth_date": "1995-03-15",
  "role": "candidate",
  ...
}
```

(valores fictícios do seed; o formato é o que importa: CPF, telefone e nascimento completos.)

---

## Evidência

| Print | O que deve aparecer |
|-------|---------------------|
| `evidence/05-cripto-lgpd/r5-admin-pii-claro.png` | Resposta 200 de `GET /api/v1/admin/users` com `cpf`, `phone` e `birth_date` em claro de vários usuários |

> Os dados do seed são fictícios; ainda assim, siga a regra de `evidence/README.md` e não publique prints com dados reais.

---

## Impacto

- **Minimização (LGPD art. 6º, III):** o papel admin gerencia contas (listar, ativar/desativar). Para isso não precisa do CPF, telefone ou nascimento completos; expô-los excede a finalidade (art. 6º, I).
- **Superfície ampliada:** um único token admin comprometido (R6 roubo de JWT, R7 abuso de conta admin, sem MFA) permite exportar em massa identificadores fortes de todos os candidatos e recrutadores.
- **Combinação de dados:** nome + CPF + nascimento + telefone é o conjunto típico para fraude de identidade e engenharia social.
- **Segurança (LGPD art. 46):** a omissão de uma medida técnica já disponível (`masking.py`) pesa contra o controlador em caso de incidente (art. 48).

**Severidade:** Média (coerente com R5 na matriz): exige conta admin, mas o volume e a sensibilidade dos dados são altos.

**Correção e reteste:** ver `fase-3b-r5-reteste.md`.
