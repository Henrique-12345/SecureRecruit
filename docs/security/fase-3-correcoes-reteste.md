# Fase 3 - Correções e plano de reteste

## Correções implementadas no código

### R1 - `/recruiters/me` e `/recruiters/me/jobs`
**Antes:** qualquer usuário autenticado (`CurrentUser`).  
**Depois:** `RecruiterUser` (papéis `recruiter` ou `admin`).  
**Arquivo:** `backend/app/api/v1/recruiters.py`  
**Proteção:** autorização por função/papel (Broken Function Level Authorization).

### R2 - Upload
**Antes:** validação por MIME + extensão + tamanho.  
**Depois:** também valida:
- assinatura `%PDF` para PDF
- ZIP/`PK` + estrutura OOXML (`[Content_Types].xml` ou `word/`) para DOCX
- consistência MIME × extensão  

**Arquivo:** `backend/app/services/resume_service.py`

### R3 - IA
**Antes:** texto do currículo ia direto ao analisador.  
**Depois:**
1. sanitização de linhas com padrões de injeção
2. pós-validação da saída (`_harden_result`): remove `OVERRIDE_OK`, limita score se flagged, registra gap/aviso  

**Arquivo:** `backend/app/services/ai_service.py`

---

## Reteste (VOCÊ executa após o deploy)

Espere o Render redeployar (push da branch / merge) ou teste localmente.

### Reteste R1
1. Login Carlos no Swagger  
2. `GET /api/v1/recruiters/me` → esperado **403**  
3. `GET /api/v1/recruiters/me/jobs` → esperado **403**  
4. Login Ana (recruiter) → mesmos endpoints → esperado **200**  
5. Prints em `evidence/03-correcao-reteste/`

### Reteste R2
1. Upload `.txt` → **400**  
2. Upload texto renomeado `.docx` → agora esperado **400** (antes era 201)  
3. Upload DOCX real válido → **201**  
4. Prints

### Reteste R3
1. Mesmo CV adversário  
2. Análise IA → não deve exaltar OVERRIDE/score forçado; pode aparecer aviso de manipulação nos gaps/notes  
3. Prints

---

## Checklist

- [x] Patch R1 no código
- [x] Patch R2 no código
- [x] Patch R3 no código
- [x] Testes automatizados adicionados
- [ ] Push / deploy
- [ ] Reteste manual R1/R2/R3 + evidências em `03-correcao-reteste/`
