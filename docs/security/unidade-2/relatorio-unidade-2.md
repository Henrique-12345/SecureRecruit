# Relatório — Unidade 2: Crypto Lab na SecureRecruit

**Projeto:** SecureRecruit (SecureAI Lab)  
**Disciplina:** Cibersegurança Aplicada a Dados e IA (CESAR School)  
**Branch:** `feature/crypto-lab-unit2`  
**Escopo:** criptografia simétrica didática + AES-256-GCM, esteganografia LSB, volume de eventos, ataques controlados, IA de anomalias e dashboard admin.

> Dados de demo são fictícios. O laboratório é **controlado** (endpoints admin) e não substitui criptografia de produção.

---

## 1. Introdução e objetivos

A Unidade 1 tratou de ameaças, exploração e endurecimento da plataforma de recrutamento. A **Unidade 2** acrescenta um **Crypto Lab** integrado à SecureRecruit para:

1. Implementar cifra simétrica com **chave dinâmica**
2. Demonstrar **XOR, substituição, permutação e blocos** (confusão/difusão)
3. Aplicar **esteganografia** após cifrar
4. Gerar e analisar **volume de eventos** (analytics)
5. Executar **ataques controlados** (força bruta truncada, diferencial, estatístico)
6. Detectar **anomalias** com regras + score (IA distinta da análise de currículo)
7. Visualizar resultados em **dashboard admin**

Objetivo pedagógico: contrastar uma cifra **didática** (Custom SPN) com uma cifra **forte** (AES-256-GCM) e discutir se o sistema fica “seguro” após o lab.

---

## 2. Arquitetura do Crypto Lab

```text
Admin UI (/admin/crypto, /admin/security-dashboard)
        ↓
FastAPI /api/v1/{crypto,stego,analytics,anomalies}
        ↓
Services: key_service · custom_cipher · aes_service · lsb_png · attacks · anomaly
        ↓
PostgreSQL: crypto_key_materials, crypto_operations, stego_artifacts,
            attack_experiments, anomaly_events (+ security_logs)
        ↓
uploads/stego/  (PNG capa e stego)
```

**Controle de acesso:** apenas papel `admin`. Candidatos/recrutadores recebem **403**.  
**Flag:** `CRYPTO_LAB_ENABLED` desliga o lab inteiro.  
**Segredo de derivação:** `CRYPTO_MASTER_SECRET` (nunca a chave crua no banco — só fingerprint + salt).

---

## 3. Algoritmo simétrico (chave dinâmica + SPN)

### 3.1 Derivação de chave

- Método: **PBKDF2-HMAC-SHA256**
- Entrada: `CRYPTO_MASTER_SECRET` + identificador do algoritmo + **salt** aleatório por material de chave
- Saída: 32 bytes; fingerprint SHA-256 armazenado em `crypto_key_materials`
- Iterações: configuráveis (`CRYPTO_PBKDF2_ITERATIONS`, padrão 100 000)

Assim a chave **não é fixa**: cada operação/material pode usar salt distinto.

### 3.2 Custom SPN (didático)

Por bloco de **16 bytes**, em **8 rodadas**:

1. **Substituição** (S-box 8→8)
2. **Permutação** (P-box de bytes)
3. **XOR** com round-key (key schedule via hashes sucessivos)

Padding PKCS#7. Formato do blob: `version || blocos cifrados`.

### 3.3 AES-256-GCM (contraste)

Implementado via biblioteca `cryptography` (AESGCM). Fornece confidencialidade + autenticidade (tag). Usado para contraste acadêmico com o SPN.

---

## 4. Difusão e confusão

| Conceito | Onde aparece no SPN |
|----------|---------------------|
| **Confusão** | S-box (relação não linear chave/plaintext → ciphertext) |
| **Difusão** | P-box + múltiplas rodadas + misturas com round-keys |

**Métrica usada:** *avalanche* — fração de bits do ciphertext que mudam ao flipar 1 bit do plaintext (ideal ≈ 0,5).

**Resultado experimental (artefato Fase 8):** avalanche do SPN didático ≈ **0,0077** (3 bits em amostra curta) — **difusão fraca**, típica de cifra pedagógica simplificada. Isso é intencional para o laboratório: permite que o ataque diferencial **exponha** a limitação.

AES-GCM não é avaliado da mesma forma (nonce aleatório por cifragem).

---

## 5. Esteganografia

Fluxo obrigatório: **plaintext → cifra → LSB em PNG**.

- Cabeçalho embutido: `SR1\0` + comprimento (4 bytes BE) + ciphertext
- Capacidade: `largura × altura × 3` bits (canais RGB)
- Persistência: `stego_artifacts` + arquivos em `STEGO_DIRECTORY`
- Extract: recupera ciphertext → decrypt com `key_id` / operação vinculada

Evidências geradas: `artifacts/02-cover-demo.png`, `02-stego-demo.png`, `02-stego-roundtrip.json`.

---

## 6. Big Data de eventos

Não há cluster Spark/Hadoop: o “volume” é **PostgreSQL + agregações**.

Fontes:

- `crypto_operations` (encrypt/decrypt/stego/métricas/ataques)
- `attack_experiments`
- `security_logs` (ex.: `login_failed`)
- `anomaly_events`

Endpoints admin: `/api/v1/analytics/events/summary`, `timeseries`, `auth/failures`, `crypto/failures`, `seed-load`.

**Seed Fase 8 (exemplo local):** 8000 crypto + 400 auth fails + 120 attacks = **8520** eventos sintéticos, suficientes para dashboard e detecção de burst.

---

## 7. IA de anomalias (Unidade 2)

Distinta da IA de currículo (Unidade 1). Detector em `AnomalyService`:

| Tipo | Ideia |
|------|--------|
| `auth_burst` | Muitas falhas de login na janela |
| `decrypt_fail_rate` | Taxa alta de decrypt com falha |
| `file_integrity` | Hash SHA-256 de currículo diverge / arquivo ausente |
| `access_pattern` | Muitos `access_denied` |
| `event_spike` | Z-score de volume horário de `CryptoOperation` |

Score 0–100 + severidade; admin pode **resolver**. No seed com 400 falhas de login, o detector criou `auth_burst` (e eventualmente `file_integrity` se arquivos seed estiverem inacessíveis).

---

## 8. Ataques controlados e resultados

Ataques **somente** contra o SPN didático, com limites (`CRYPTO_LAB_MAX_SEARCHABLE_BITS`, `CRYPTO_LAB_MAX_ATTACK_ATTEMPTS`).

### 8.1 Força bruta (chave truncada)

Busca apenas os N bits baixos da chave (lab). Artefato:

| Métrica | Valor |
|---------|-------|
| Bits | 10 |
| Encontrou | sim (401 / 1024 tentativas) |
| Tempo | ~24 ms |
| Extrapolação 256-bit | ~10⁶⁵ anos (inviável) |
| Label | eficaz *no lab truncado* |

Conclusão: BF “funciona” no espaço artificial; no espaço real continua impraticável.

### 8.2 Diferencial

Flip de 1 bit no plaintext; mede avalanche/Hamming.

| Métrica | Valor |
|---------|-------|
| Avalanche | ≈ 0,0077 |
| Hamming | 3 bits |
| Label | eficaz em expor difusão fraca |
| Score eficácia | ≈ 0,98 |

### 8.3 Estatístico

Entropia / χ² vs uniforme no ciphertext.

| Métrica | Valor |
|---------|-------|
| Entropia | ≈ 5,41 / 8 bits |
| χ² | ≈ 259 |
| Bytes únicos | 44 (em 49 bytes) |

Amostra curta → estatística limitada; ainda assim mostra desvio do ideal uniforme.

---

## 9. Avalanche, padrões e qual ataque foi mais eficaz?

| Ataque | O que prova | Eficácia no lab |
|--------|-------------|-----------------|
| **Diferencial** | Difusão fraca do SPN | **Mais revelador** sobre qualidade da cifra |
| **BF truncado** | Custo de busca vs. chave completa | Eficaz só no cenário artificial |
| **Estatístico** | Estrutura residual no ciphertext | Moderado (amostra pequena) |

**Resposta objetiva:** o ataque **diferencial** foi o mais útil pedagogicamente — quantifica a falha de avalanche do SPN. O BF ilustra escala. O estatístico complementa.

Padrões: ciphertext SPN em amostras curtas não atinge entropia ~8; avalanche longe de 0,5.

---

## 10. O sistema é seguro? Justificativa

**Parcialmente, com ressalvas claras.**

### O que está em boa direção

- AES-256-GCM disponível como referência forte
- Chaves derivadas dinamicamente; fingerprint sem chave em claro
- Lab isolado a **admin**; flag de desligamento
- Limites de payload/BF; auditoria sem plaintext
- JWT + Argon2id + controles da Unidade 1 no restante do app
- Stego só após cifrar (ocultação ≠ confidencialidade sozinha)

### O que **não** torna o produto “criptograficamente seguro”

- O **Custom SPN é didático** (difusão fraca medida)
- Esteganografia LSB é frágil a análise forense
- `CRYPTO_MASTER_SECRET` / JWT em env — gestão de segredos precisa ser rigorosa em produção
- Volume “Big Data” é analítico, não um SOC completo
- Detector de anomalias baseado em regras pode ter falsos positivos/negativos

**Síntese para a banca:** a SecureRecruit **não depende** do SPN para proteger PII em produção; o Crypto Lab **ensina** propriedades e ataques. Para dados reais, usar primitivas maduras (AES-GCM/TLS), KMS e os controles já discutidos na Unidade 1 (LGPD, authz, upload, IA).

---

## 11. Conclusão e referências

A Unidade 2 entregou um laboratório ponta a ponta na SecureRecruit: cifra (SPN + AES), stego LSB, ataques, métricas, analytics, anomalias e UI admin, com hardening mínimo (Fase 10) e evidências em `docs/security/evidence/unidade-2/`.

### Referências (seleção)

- Stallings, W. *Cryptography and Network Security*
- NIST SP 800-38D (GCM)
- NIST SP 800-132 (PBKDF2)
- Anderson, R. *Security Engineering* (esteganografia / threat model)
- Documentação interna: `docs/security/unidade-2/`, `docs/security/fase-5-criptografia-lgpd.md`

---

## 12. Anexo — evidências

| Pasta / artefato | Conteúdo |
|------------------|----------|
| `evidence/unidade-2/artifacts/*.json` | Round-trip, stego, 3 ataques, avalanche |
| `evidence/unidade-2/artifacts/*-demo.png` | Capa e stego gerados |
| `evidence/unidade-2/01-cifra` … `06-anomalias` | Locais para **prints da UI** (equipe) |
| Checklists `fase-0` … `fase-10` | Rastreio de entrega |

**Pendência da equipe:** anexar screenshots da demo oral nas pastas 01–06.
