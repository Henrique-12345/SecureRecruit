# Fase 2c - Exploração controlada (R3b: keyword stuffing no analisador de IA)

**Formato:** Vulnerabilidade → Método → Evidência → Impacto

**Categoria do edital:** vulnerabilidade relacionada ao uso de IA (manipulação da avaliação automatizada)
**Risco da matriz:** R3 - Prompt injection / manipulação altera análise/score (`fase-1-threat-model-matriz-riscos.md`)
**Ambiente:** SecureRecruit, analisador heurístico local (sem `AI_API_KEY`), contas demo (`Demo@1234`)

> Teste controlado na própria aplicação da equipe, para o SecureAI Lab.

---

## Por que esta fase existe

Na Fase 2 (`fase-2-resultados.md`, `fase-4-seguranca-ia.md`), a prompt injection **não funcionou** contra o analisador local: a heurística não obedece instruções, então o score não foi forçado. Faltava demonstrar um ataque de IA que **funciona de fato** contra o modelo em uso. O keyword stuffing preenche esse passo: ele explora a lógica de pontuação, não a obediência a instruções.

---

## Vulnerabilidade

Em `backend/app/services/ai_service.py`, `_local_analyze` calculava o `compatibility_score` **apenas pela sobreposição** entre as competências conhecidas (`KNOWN_SKILLS`) presentes em qualquer lugar do texto e as exigidas em `job.requirements`:

```python
overlap = len(set(matched) & set(required_hint))
score = round((overlap / max(len(required_hint), 1)) * 100, 1)
```

Não havia distinção entre uma skill **citada numa experiência** e uma skill **apenas listada**. Basta copiar os requisitos da vaga para o currículo e o score chega a 100.

O mesmo acontecia em vagas sem skills conhecidas nos requisitos (`score = 40 + 5 × skills`): listar as 27 skills conhecidas dava 100.

---

## Método

1. Montar um DOCX com **apenas** os requisitos da vaga seed "DevOps Engineer" (`Docker, Kubernetes, CI/CD, Linux, AWS`), sem nenhuma experiência:
   ```text
   João Stuffing
   Skills: Docker, Kubernetes, CI/CD, Linux, AWS
   kubernetes aws linux ci/cd docker
   ```
2. Swagger → login `carlos.candidate@example.com` / `Demo@1234` → **Authorize**.
3. `POST /api/v1/resumes` (multipart) com o DOCX → anotar `id`.
4. `GET /api/v1/jobs` → anotar `id` da vaga "DevOps Engineer".
5. `POST /api/v1/ai/match-resume-job` com `{"resume_id": "...", "job_id": "..."}`.
6. Observar `compatibility_score`, `gaps` e `compatibility_notes`.

> **Atenção:** `POST /api/v1/ai/analyze-resume` **não aceita `job_id`** (o schema `AnalyzeResumeRequest` só tem `resume_id`) e devolve `compatibility_score: null`. O score em relação a uma vaga só existe em `POST /api/v1/ai/match-resume-job`.

**Resultado observado (antes da correção):**

```json
{
  "compatibility_score": 100.0,
  "result": {
    "gaps": ["Informações de formação ou métricas de impacto poderiam ser mais detalhadas"],
    "compatibility_notes": "Matched skills: aws, ci/cd, docker, kubernetes, linux. Potential gaps: none identified.",
    ...
  }
}
```

Currículo sem nenhuma experiência → **100/100, sem gaps de skill, sem aviso**.

---

## Evidência

| Print | O que deve aparecer |
|-------|---------------------|
| `evidence/04-ia/r3-stuffing-score-inflado.png` | Resposta 201 de `match-resume-job` com `compatibility_score: 100.0` para o CV só com lista de palavras-chave |

(Opcional: incluir no print ou num segundo print o conteúdo do DOCX, mostrando que não há experiência.)

---

## Impacto

| Dimensão | Impacto |
|----------|---------|
| Integridade | **Alto**: o score, usado para priorizar candidatos, é trivialmente forjável |
| Negócio | Candidatos sem qualificação sobem no ranking; candidatos honestos com currículo narrativo ficam abaixo |
| Probabilidade | **Alta**: não exige conhecimento técnico; "copiar os requisitos para o CV" é prática conhecida para burlar ATS |
| LGPD | Art. 20: decisões baseadas em tratamento automatizado podem ser revisadas; um score manipulável sem aviso de revisão humana fragiliza a transparência e a qualidade da decisão (art. 6º, V e VI) |

**Contraste com prompt injection:** a injection depende de um LLM que obedeça texto, e com a heurística local o ataque falhou. O stuffing **funciona contra a heurística** e, em grau menor, contra LLMs, que também tendem a supervalorizar a sobreposição de termos.

**Correção e reteste:** ver `fase-3c-r3-reteste.md`.
