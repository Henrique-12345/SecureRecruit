# Fase 3b - Correção e reteste (R5: exposição de PII)

Referência da exploração: `fase-2b-r5-pii.md`

## Correção implementada no código

### R5 - Respostas administrativas de usuário
**Antes:** `UserAdminRead(UserRead)` retornava `cpf`, `phone` e `birth_date` em claro em `GET /admin/users`, `GET /admin/users/{id}` e `PATCH /admin/users/{id}/status`.
**Depois:** `UserAdminRead` é um schema próprio, construído por `UserAdminRead.from_user(user)`, que reutiliza `app/utils/masking.py`:

| Campo | Antes | Depois |
|-------|-------|--------|
| `cpf` | `123.456.789-00` | `***.***.***-00` (`mask_cpf`) |
| `phone` | `(81) 98765-4321` | `(81) *****-4321` (`mask_phone`) |
| `birth_date` | `1995-07-14` | removido → `birth_year: 1995` |
| `name`, `email`, `role`, `is_active` | claro | claro (necessários para gerir contas) |

**Arquivos:**
- `backend/app/schemas/user.py`: novo `UserAdminRead` + `from_user`
- `backend/app/api/v1/admin.py`: rotas de usuário usam `UserAdminRead.from_user(...)`
- `tests/security/test_pii_masking.py`: testes de regressão

**Decisões:**
- **Nascimento reduzido ao ano:** contexto administrativo suficiente (ex.: maioridade aproximada) sem o dado completo, que combinado com nome/CPF facilita a identificação.
- **Mascaramento na construção, não em serializer:** o FastAPI revalida o `response_model`, e `mask_phone` não é idempotente (mascarar duas vezes perderia o DDD). Aplicar em `from_user` garante uma única passagem.
- **Não alterado:** `GET /users/me`, `/auth/me` e `/recruiters/me` seguem com dados completos do próprio titular (LGPD art. 18, II), e `GET /candidates/{id}` segue com `CandidatePublicRead`.

**Base legal:** LGPD art. 6º, III (minimização) e art. 46 (medidas técnicas de segurança).

---

## Teste automatizado

`tests/security/test_pii_masking.py`:
1. `test_admin_user_list_masks_pii`: admin lista usuários; CPF e telefone completos não aparecem no corpo; o CPF contém `***` e termina em `00`; o telefone termina em `4321`; não há `birth_date`, só `birth_year`.
2. `test_admin_user_detail_masks_pii`: mesmas verificações em `GET /admin/users/{id}`.
3. `test_owner_still_sees_own_pii_in_clear`: `GET /users/me` e `/auth/me` continuam retornando CPF, telefone e `birth_date` completos para o titular.

Resultado local: `pytest -q` → **11 passed**.

---

## Reteste manual

1. Swagger → login `admin@example.com` / `Demo@1234` → **Authorize**.
2. `GET /api/v1/admin/users` → esperado **200** com `cpf` no formato `***.***.***-NN`, `phone` como `(DD) *****-NNNN` e `birth_year` no lugar de `birth_date`.
3. `GET /api/v1/admin/users/{id}` de um candidato → mesmo mascaramento.
4. Login `carlos.candidate@example.com` → `GET /api/v1/users/me` → esperado CPF/telefone/nascimento **completos** (dado próprio).
5. Prints.

| Etapa | Antes | Depois | Print |
|-------|-------|--------|-------|
| Admin → `GET /admin/users` | CPF/telefone/nascimento em claro | mascarados / só ano | `evidence/05-cripto-lgpd/r5-admin-pii-mascarado.png` |
| Titular → `GET /users/me` | completo | completo (inalterado) | (opcional) |

> Na tela do admin no frontend (`/admin/users/:id`), CPF e telefone passam a aparecer mascarados; nenhuma mudança de frontend foi necessária.

---

## Checklist

- [x] Patch R5 no código
- [x] Testes automatizados adicionados
- [ ] Push / deploy
- [ ] Reteste manual + `r5-admin-pii-claro.png` e `r5-admin-pii-mascarado.png` em `evidence/05-cripto-lgpd/`
