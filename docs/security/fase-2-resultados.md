# Fase 2 - Resultados da exploração controlada

## R1 - Autorização

| Teste | Resultado | Interpretação |
|-------|-----------|---------------|
| Candidate → dados de outro candidate | **403** | Controle IDOR eficaz |
| Candidate → `/admin/*` | **403** | Controle de papel eficaz |
| Candidate → `GET /recruiters/me` | **200** | **Falha:** Broken Function Level Authorization |
| Candidate → `GET /recruiters/me/jobs` | **200** (lista vazia) | Mesma falha de namespace/papel |

**Evidências:** `evidence/02-exploracao/r1-*.png`

**Impacto do achado `/recruiters/*`:** baixo/médio - não vaza dados de terceiros, mas quebra a expectativa de que rotas de recrutador exijam papel `recruiter`.

---

## R2 - Upload

| Teste | Resultado | Interpretação |
|-------|-----------|---------------|
| Upload `.txt` | **400** | Filtro de tipo/extensão OK |
| Upload texto renomeado para `.docx` | **201** | **Falha:** validação só por metadados |

**Evidências:** `r2_cvctxt.png`, `r2_cvdocx.png`

**Impacto:** armazenamento de arquivo não conforme; risco de processar conteúdo inesperado.

---

## R3 - IA / prompt injection

| Teste | Resultado | Interpretação |
|-------|-----------|---------------|
| Currículo com instruções adversárias | Score/comportamento **não** forçado a 100% | Heurística local resistiu neste caso |

**Evidências:** `r3_promptmalicioso.png`, `r3_resultadoprompt.png`

**Impacto residual:** arquitetura ainda injeta texto do CV no fluxo de IA; risco permanece se houver LLM remoto. Mitigação reforçada na Fase 3.

---

## Conclusão Fase 2

Achados prioritários para correção:
1. Restringir `/recruiters/*` por papel
2. Validar conteúdo real de PDF/DOCX no upload
3. Sanitizar/filtrar padrões de manipulação no pipeline de IA
