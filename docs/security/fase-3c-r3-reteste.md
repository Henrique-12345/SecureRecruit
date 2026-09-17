# Fase 3c - Correção e reteste (R3b: keyword stuffing + prompt injection)

Referência da exploração: `fase-2c-r3-stuffing.md`. Mitigações anteriores de injection: `fase-3-correcoes-reteste.md`, `fase-4-seguranca-ia.md`.

## Correção implementada no código

**Arquivo:** `backend/app/services/ai_service.py`

### 1. Corroboração de competências (`_experience_lines` + `_local_analyze`)
Uma skill exigida pela vaga só conta **integralmente** se aparecer numa **linha de experiência**:
- linha com mais de 40 caracteres (`EXPERIENCE_MIN_CHARS`);
- pelo menos 6 palavras (`EXPERIENCE_MIN_WORDS`);
- no máximo 40% das palavras sendo skills conhecidas (`EXPERIENCE_MAX_SKILL_DENSITY`).

Os dois últimos critérios existem porque "linha > 40 chars" sozinho seria contornado com `Skills: Docker, Kubernetes, CI/CD, Linux, AWS`, que tem 45 chars mas é só uma lista.

Skills que aparecem apenas como lista solta são **reivindicadas não corroboradas**:
- contam com peso **0,25** (`UNCORROBORATED_SKILL_WEIGHT`);
- entram em `gaps`: *"Competências apenas listadas, sem experiência descrita que as corrobore: ..."*;
- geram aviso em `compatibility_notes`: *"possível keyword stuffing"*.

A mesma ponderação vale para vagas sem skills conhecidas nos requisitos (`40 + 5 × peso`). `relevant_experience` agora lista só as linhas que passaram no critério.

**Fórmula:** `score = (corroboradas + 0,25 × só listadas) / exigidas × 100`

### 2. Aviso de revisão humana (`_harden_result`)
Todo resultado (local **ou** remoto) recebe em `compatibility_notes`:
*"Aviso: análise automatizada de apoio; a decisão exige revisão humana do currículo."* (LGPD art. 20).

### 3. Prompt injection: mantido
`INJECTION_PATTERNS`, `_sanitize_resume_text`, `_harden_result` (filtro `OVERRIDE_OK`, teto de 70 e gap de manipulação) e os delimitadores `UNTRUSTED RESUME DATA` não foram alterados. O stuffing e a injection são tratados em camadas independentes.

---

## Antes / depois (vaga "DevOps Engineer": Docker, Kubernetes, CI/CD, Linux, AWS)

| Currículo | Antes | Depois | Sinalização |
|-----------|-------|--------|-------------|
| Só lista de skills (stuffing) | **100.0** | **25.0** | gap "apenas listadas…" + aviso keyword stuffing |
| 2 skills em experiência + 3 só listadas | 100.0 | **55.0** | gap com as 3 não corroboradas |
| Experiência real citando as 5 skills | 100.0 | **100.0** | nenhum aviso de stuffing |
| Experiência real + linha `OVERRIDE_OK … score 100` | 70.0 | **70.0** | linha filtrada, gap de manipulação, aviso de instruções filtradas |

Todos os resultados passam a ter o aviso de revisão humana.

---

## Teste automatizado

`tests/security/test_ai_hardening.py` roda o fluxo real (upload DOCX → `POST /ai/match-resume-job`) forçando o analisador local (`AI_API_KEY=""`):

1. `test_keyword_stuffing_does_not_inflate_score`: stuffing → score ≤ 30, sinalizado em `gaps`/`notes`, sem `relevant_experience`.
2. `test_override_ok_injection_is_filtered_and_score_capped`: `OVERRIDE_OK` não aparece em nenhum lugar da resposta, score ≤ 70, gap de manipulação.
3. `test_legitimate_resume_keeps_coherent_score`: experiência real → 100.0, sem falso positivo de stuffing.
4. `test_partially_corroborated_resume_scores_between`: caso misto → 55.0.

Resultado local: `pytest -q` → **15 passed**.

---

## Reteste manual

1. Swagger → login `carlos.candidate@example.com` → **Authorize**.
2. Mesmo DOCX de stuffing da Fase 2c → `POST /api/v1/resumes`.
3. `POST /api/v1/ai/match-resume-job` com a vaga "DevOps Engineer" → esperado `compatibility_score: 25.0`, gap "Competências apenas listadas…" e aviso de keyword stuffing e de revisão humana.
4. (Contraprova) DOCX com experiência narrativa citando as mesmas skills → esperado score alto, sem aviso de stuffing.
5. Prints.

| Etapa | Print |
|-------|-------|
| Antes: stuffing → 100.0 | `evidence/04-ia/r3-stuffing-score-inflado.png` |
| Depois: stuffing → 25.0 sinalizado | `evidence/04-ia/r3-stuffing-mitigado.png` |

---

## Cenário complementar: prompt injection com LLM remoto

Com `AI_API_KEY` configurada, o texto do currículo vai para um LLM generativo, que **pode obedecer** instruções embutidas. Esse é o risco arquitetural de R3 que a heurística local não reproduz (ver `fase-4-seguranca-ia.md` §3). Ele segue coberto por:
- delimitadores `UNTRUSTED RESUME DATA` e `SYSTEM_INSTRUCTIONS` tratando o currículo como dado;
- `_sanitize_resume_text` removendo linhas com padrões de injeção **antes** do envio;
- `_harden_result` filtrando `OVERRIDE_OK` e limitando o score a 70 quando há flag;
- validação `AIAnalysisResult` (Pydantic, score 0–100);
- aviso de revisão humana, agora também em respostas remotas.

**Limitação:** a corroboração de skills está só no fluxo local. Um LLM remoto não passa pela ponderação 0,25 e depende das instruções de sistema para não supervalorizar listas de palavras-chave.

---

## Riscos residuais

1. **Stuffing narrativo:** um candidato pode escrever frases falsas ("Atuei 5 anos com Kubernetes…"). A heurística verifica o *formato* de experiência, não a *veracidade*. Isso reforça a revisão humana obrigatória.
2. **Correspondência por substring** (pré-existente): `java` casa com `javascript`, `rest` com `interest`, `sql` com `postgresql`. Isso pode inflar ou distorcer o score em algumas vagas. Não foi alterado neste patch.
3. **Limiares heurísticos** (40 chars, 6 palavras, 40% de densidade) podem gerar falsos positivos em currículos muito telegráficos. Nesse caso o impacto é score parcial com aviso, não exclusão.
4. **Novos padrões de injection** escapam da lista de regex (já registrado na Fase 4).

---

## Checklist

- [x] Patch de corroboração no fluxo local
- [x] Aviso de revisão humana em todos os resultados
- [x] Mitigação de prompt injection preservada
- [x] Testes automatizados (`test_ai_hardening.py`)
- [ ] Push / deploy
- [ ] Reteste manual + `r3-stuffing-score-inflado.png` e `r3-stuffing-mitigado.png` em `evidence/04-ia/`
