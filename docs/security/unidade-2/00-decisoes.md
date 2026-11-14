# Unidade 2 — Decisões de projeto (Fase 0)

**Branch:** `feature/crypto-lab-unit2`  
**Base:** `main` (SecureRecruit pós-Unidade 1)

## Decisões tomadas

| Tema | Decisão | Justificativa |
|------|---------|---------------|
| Tipo de dado | **Texto + arquivo simples** | Alinha com a SecureRecruit (mensagens/metadados + arquivos já existentes) |
| Cifra didática | **Custom SPN** (substituição + permutação + XOR + blocos + rodadas) | Atende XOR/sub/perm/blocos, difusão/confusão e ataques do edital |
| Cifra “forte” | **AES-256-GCM** (biblioteca padrão) | Contraste acadêmico com o slide de arquitetura (AES-256) e demonstração de integridade autenticada |
| Chave | **Dinâmica** via PBKDF2/HKDF a partir de `CRYPTO_MASTER_SECRET` + salt por operação | Chave não fixa; influencia a cifragem; fingerprint no banco, não a chave em claro |
| Esteganografia | **LSB em PNG** após cifrar o payload | Fluxo: dados → cifra → oculta em imagem |
| Big Data | Tabelas `crypto_operations`, `attack_experiments`, `anomaly_events` + reuso de `security_logs` | Volume experimental + analytics |
| IA Unidade 2 | **Detector de anomalias** (regras + score; Isolation Forest opcional) | Diferente da IA de currículo da Unidade 1 |
| Acesso | Endpoints do Crypto Lab só para **admin** | Lab controlado, sem expor ataques a candidatos |
| Dashboard | Novas telas admin: Crypto Lab + Security Dashboard | Requisitos de visualização de ataques/anomalias |

## Fora de escopo nesta entrega (explícito)

- Criptografia assimétrica completa (além do TLS já usado em produção)
- Esteganografia em vídeo
- Cluster Big Data real (Spark/Hadoop) — usamos PostgreSQL + agregações + seed de volume

## Arquitetura-alvo

```text
Entrada (texto/arquivo)
  → Criptografia (custom SPN e/ou AES-256-GCM)
  → Esteganografia LSB (PNG)
  → Eventos (crypto_operations / attacks / security_logs)
  → IA de anomalias
  → Dashboard admin
```
