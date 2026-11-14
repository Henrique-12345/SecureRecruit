# Roteiro de slides — Unidade 2 (≈ 15 minutos)

**Demo ao vivo sugerida:** cifrar → stego → diferencial → dashboard → anomalia.

Use este roteiro no Google Slides / PowerPoint. Cada bloco = 1–2 slides.

---

## Slide 1 — Título (30 s)

- SecureRecruit · SecureAI Lab · Unidade 2  
- Crypto Lab: cifra, stego, ataques, anomalias, dashboard  
- Equipe + data

## Slide 2 — Objetivos (1 min)

- O que a Unidade 2 acrescenta à plataforma  
- Lab **admin-only**, chave dinâmica, contraste SPN × AES

## Slide 3 — Arquitetura (1 min)

- Diagrama: UI → API → services → Postgres / uploads/stego  
- Tabelas novas: operations, stego, attacks, anomalies

## Slide 4 — Custom SPN (1,5 min)

- Blocos 16 B · S-box · P-box · XOR · 8 rodadas · PKCS7  
- PBKDF2 + salt → fingerprint (sem chave no banco)

## Slide 5 — AES-256-GCM (45 s)

- Contraste: autenticado, biblioteca padrão  
- “Produção usaria isto; SPN é pedagógico”

## Slide 6 — DEMO: Cifrar / Decifrar (1,5 min)

- `/admin/crypto/encrypt`  
- SPN round-trip + mencionar AES  
- **Print** → pasta `01-cifra`

## Slide 7 — DEMO: Esteganografia (1,5 min)

- `/admin/crypto/stego`  
- PNG capa → embed → extract  
- **Print** antes/depois → `02-stego`

## Slide 8 — Difusão / Avalanche (1 min)

- Ideal ≈ 0,5 · SPN lab ≈ 0,008 (difusão fraca medida)  
- `/admin/crypto/avalanche`  
- **Print** → `04-avalanche`

## Slide 9 — DEMO: Ataque diferencial (1,5 min)

- `/admin/crypto/attacks` aba Diferencial  
- Mostrar score / label “difusão fraca”  
- Mencionar BF truncado + estatístico em 15 s  
- **Print** → `03-ataques`

## Slide 10 — Qual ataque foi mais eficaz? (1 min)

- Tabela: Diferencial > BF lab > Estatístico (nesta demo)  
- BF: ok no truncado; 256-bit inviável

## Slide 11 — Big Data + Dashboard (1,5 min)

- `/admin/security-dashboard`  
- KPIs 24h · série temporal · botão “Gerar carga + detector”  
- **Print** → `05-dashboard`

## Slide 12 — IA de anomalias (1 min)

- Regras + z-score · `auth_burst`  
- `/admin/anomalies` · resolver  
- **Print** → `06-anomalias`

## Slide 13 — O sistema é seguro? (1,5 min)

- Sim para o **desenho do lab** (admin, AES, limites, Unidade 1)  
- Não se confundir SPN/LSB com proteção de PII real  
- Mensagem única para a banca

## Slide 14 — Conclusão (45 s)

- Entregáveis: código + checklists + evidências  
- Próximos passos: prints finais · merge · deploy (Fase 10)

## Slide 15 — Q&A / Referências (se sobrar tempo)

- Stallings · NIST GCM/PBKDF2 · docs internos Unidade 2

---

## Cronômetro rápido

| Minuto | Bloco |
|--------|--------|
| 0–2 | Título + objetivos + arquitetura |
| 2–6 | SPN/AES + demos cifra/stego |
| 6–10 | Avalanche + ataques |
| 10–13 | Dashboard + anomalias |
| 13–15 | Segurança? + conclusão |

## Checklist pré-apresentação

- [ ] API + front locais (ou produção) no ar  
- [ ] Login admin  
- [ ] PNG de capa pronto (`uploads/stego/cover_demo.png`)  
- [ ] Prints nas pastas 01–06  
- [ ] Relatório `relatorio-unidade-2.md` revisado pela equipe
