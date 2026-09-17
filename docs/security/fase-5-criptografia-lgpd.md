# Fase 5 - Estratégia Criptográfica, LGPD e Anonimização

**Projeto:** SecureRecruit (SecureAI Lab)
**Disciplina:** Cibersegurança Aplicada a Dados e IA - CESAR School
**Serviços de referência:** `core/security.py`, `services/hash_service.py`, `utils/masking.py`, `services/resume_service.py`, `services/signature_service.py`

Esta fase atende às exigências do edital de **justificar tecnicamente** o uso de criptografia e de demonstrar **proteção de dados / LGPD / anonimização**. Nenhuma justificativa aqui é do tipo "escolhemos porque é mais seguro": cada decisão é ligada a uma ameaça, a um requisito de propriedade (confidencialidade, integridade, autenticidade) e a um trade-off explícito.

---

## 1. Modelo de dados e classificação (base para as decisões)

| Dado | Sensibilidade | Propriedade crítica | Onde vive |
|------|---------------|---------------------|-----------|
| Senha | Credencial | Confidencialidade (irreversível) | `users.password_hash` |
| Token de sessão (JWT) | Segredo de sessão | Autenticidade + integridade | Cliente (localStorage) |
| CPF, telefone, email | Pessoal | Confidencialidade | `users`, `candidate_profiles` |
| Currículo (arquivo) | Pessoal / documento | Integridade + confidencialidade | `uploads/`, `resumes` |
| Dados em trânsito | Todos os acima | Confidencialidade + integridade | Rede (cliente↔API) |
| Logs de auditoria | Operacional | Integridade + rastreabilidade | `security_logs` |

A escolha de mecanismo criptográfico segue diretamente desta classificação: **o que precisa ser verificado mas nunca revelado** usa hash; **o que precisa ser comparado mas nunca reconstruído** usa hash com sal (senha); **o que precisa provar autoria/integridade a terceiros** usa assinatura assimétrica; **o que precisa ser lido de volta pelo próprio sistema** usaria cifra simétrica.

---

## 2. Onde utilizar criptografia simétrica

**Uso atual:** o token de sessão (JWT) é assinado com **HS256 = HMAC-SHA256**, que é um MAC de chave simétrica. A mesma `JWT_SECRET_KEY` que gera o token o verifica (`core/security.py`).

**Justificativa técnica:**
- O emissor e o verificador do token são **o mesmo serviço** (a API FastAPI). Não há terceiro que precise verificar o token sem poder emiti-lo. Nesse cenário, HMAC simétrico é a escolha correta: mais simples, mais rápido e sem a complexidade de par de chaves.
- Migrar para assinatura assimétrica (RS256/ES256) só se justifica quando **verificadores não confiáveis** precisam validar o token sem poder forjá-lo (ex.: múltiplos microserviços, gateways externos). Não é o caso aqui - por isso a escolha por HS256 é técnica, não por conveniência.

**Onde a cifra simétrica seria aplicada em evolução futura:** proteção de **PII em repouso** (ex.: cifrar CPF com AES-256-GCM, chave via KMS/env), quando o próprio sistema precisa **ler de volta** o dado. Hoje o CPF é protegido por mascaramento na saída (§8); a cifra em repouso está documentada como recomendação (§11) por implicar migração de schema e gestão de chave de dados adicional.

---

## 3. Onde utilizar criptografia assimétrica

**Estado atual:** a versão entregue **não usa** criptografia assimétrica - todos os mecanismos em uso são simétricos (HMAC no JWT) ou de hash (Argon2id, SHA-256). Esta seção justifica **onde** ela se aplicaria e **por que** a escolha atual é adequada ao escopo (o edital pede justificar onde utilizar, não implementar tudo).

**Onde se aplicaria:** **assinatura digital do currículo**. No upload já se calcula o SHA-256 do arquivo (integridade); um passo assimétrico assinaria esse hash com a **chave privada** do servidor, permitindo que qualquer parte verificasse a assinatura com a **chave pública** sem poder forjá-la.

**Justificativa técnica:**
- A propriedade que a assimétrica traz e a simétrica não é **autenticidade verificável por terceiros**: **verificar ≠ poder assinar**. Com HMAC, quem verifica também poderia forjar; com assinatura, não.
- Se implementada, **Ed25519** seria a escolha (em vez de RSA-2048): assinaturas curtas e determinísticas, verificação rápida, sem padding frágil (PKCS#1v1.5), chaves pequenas.
- **Por que não foi adotada nesta versão:** o SHA-256 + endpoint de verificação de integridade já cobre a detecção de adulteração no escopo acadêmico controlado; a assinatura acrescentaria autenticidade de origem, que não é exigência mínima do projeto. Fica como recomendação futura (roteiro no §11 e §5 da auditoria).

**Por que o JWT usa simétrica (HS256) e não assimétrica:** o token é emitido e verificado **pelo mesmo serviço** (a API). Não há verificador não confiável que precise validar sem poder emitir; nesse cenário o MAC simétrico é a escolha correta, e migrar para RS256/ES256 só se justificaria com múltiplos serviços/gateways externos - o que não é o caso.

---

## 4. Onde utilizar funções hash

Duas funções hash, com finalidades **distintas** e deliberadas:

| Função | Uso | Por quê |
|--------|-----|---------|
| **SHA-256** | Integridade de arquivo de currículo (`hash_service.py`) | Rápido, é o que se quer para detectar alteração de conteúdo; não precisa ser lento porque não protege segredo |
| **Argon2id** | Hash de senha (`core/security.py`) | É o oposto: precisa ser **lento e caro em memória** para resistir a ataque de força bruta/GPU |

**Ponto técnico central:** usar SHA-256 para senha seria um **erro** (rápido demais → força bruta viável), e usar Argon2id para integridade de arquivo seria desperdício. A separação demonstra entendimento de que "hash" não é uma coisa só.

---

## 5. Como proteger senhas

- Algoritmo: **Argon2id** via `passlib` (`CryptContext(schemes=["argon2"])`).
- Propriedades: sal único por senha (embutido no hash), custo de memória e tempo configurável, resistência a GPU/ASIC e a side-channel (variante `id`).
- Nunca há senha em claro no banco nem em log; a verificação usa `verify_password` (comparação em tempo constante do passlib).

**Justificativa:** Argon2id venceu a Password Hashing Competition e é a recomendação atual da OWASP para hashing de senha. A escolha é ligada à ameaça (vazamento do banco → força bruta offline), não à conveniência.

---

## 6. Como proteger dados em trânsito

- **TLS/HTTPS** em toda a comunicação cliente ↔ API em produção (Vercel e Render terminam TLS).
- CORS restrito por allowlist + regex de domínio Vercel (`main.py`), reduzindo origem de requisições cross-site.

**Justificativa:** o token JWT e a PII trafegam pela rede; sem TLS, um atacante na rede (MITM) leria credenciais e dados. HTTPS garante confidencialidade e integridade do canal. Em desenvolvimento local (HTTP), o risco é aceito e documentado por ser ambiente controlado.

---

## 7. Quando utilizar assinatura digital

**Onde se aplicaria na SecureRecruit:** para dar **autenticidade de origem** ao hash do currículo - provar que aquele arquivo, com aquele hash, foi registrado pela plataforma e não foi trocado depois.

**Diferença em relação ao que já existe:** o SHA-256 (implementado) detecta *se o arquivo mudou*, mas qualquer um pode recomputar um novo hash para um arquivo trocado. Uma **assinatura** (não implementada) amarraria o hash a uma **autoria** - um terceiro não produziria assinatura válida sem a chave privada. É a diferença entre *"o arquivo mudou?"* (hash) e *"quem atesta este arquivo?"* (assinatura).

**Decisão para esta versão:** a integridade exigida pelo projeto é atendida por SHA-256 + endpoint de verificação; a assinatura digital fica documentada como **recomendação futura** (Ed25519 sobre o hash do currículo, verificável pela chave pública). Não foi implementada por não ser exigência mínima e por evitar risco de deploy próximo à entrega.

---

## 8. Como proteger dados sensíveis (em uso e na saída)

- **Mascaramento** (`utils/masking.py`): `mask_cpf` (`***.***.***-XX`), `mask_email` (`a****@dominio`), `mask_phone` (`(XX) *****-XXXX`), `mask_name`. **Aplicado nas respostas administrativas de usuário** (`GET /admin/users`, `/admin/users/{id}`): o administrador gerencia contas e não precisa do CPF/telefone completos - minimização LGPD. (Correção da vulnerabilidade **R5**: o utilitário existia mas não estava sendo aplicado; a exposição de PII em claro no admin foi fechada.)
- **Minimização em respostas**: schemas Pydantic controlam quais campos saem da API por papel. `GET /candidates/{id}` usa `CandidatePublicRead`, que já **não** inclui CPF - recrutador vê perfil profissional, não documento.
- **Dados próprios completos**: o titular vê o próprio CPF em `GET /users/me` (acesso legítimo aos próprios dados); o mascaramento incide onde o dado é de terceiros.
- **Autorização como controle primário de confidencialidade**: PII de terceiros é bloqueada por ownership/role antes de qualquer serialização.
- **Logs sem segredo**: `security_logs` registra ação/resultado/IP, não senha nem token.
- **Pseudonimização**: UUID como referência de recurso, em vez de expor identidade direta.

**Justificativa:** defesa em profundidade - autorização impede acesso indevido; mascaramento reduz exposição mesmo em telas legítimas de admin; minimização reduz a superfície de vazamento. Cada camada cobre uma falha da outra.

---

## 9. Como ocorre o gerenciamento de chaves

| Chave | Tipo | Armazenamento | Rotação / escopo |
|-------|------|---------------|------------------|
| `JWT_SECRET_KEY` | Simétrica (HMAC) | Variável de ambiente (Render), fora do repositório | Rotacionável; rotação invalida sessões vigentes (aceitável) |
| Par Ed25519 (assinatura) | Assimétrica | Privada em env/secret do servidor; pública publicável | Identificador de chave permite rotação com verificação de assinaturas antigas |
| Segredos de banco (`DATABASE_URL`) | Credencial | Variável de ambiente | Gerida pelo provedor |

**Princípios aplicados:** (1) segredos **nunca** no código/repo (`.gitignore` + `.env.example` sem valores reais); (2) separação de segredo por finalidade (token ≠ assinatura ≠ banco); (3) chave privada de assinatura nunca sai do servidor, só a pública é distribuída; (4) `key_id` permite rotação sem invalidar histórico. **Limitação honesta:** não há HSM/KMS dedicado nem rotação automática - adequado ao escopo acadêmico, citado como evolução.

---

## 10. LGPD e privacidade

| Princípio LGPD | Como se aplica na SecureRecruit |
|----------------|--------------------------------|
| Finalidade | Dados usados apenas para o fluxo de recrutamento simulado |
| Minimização | Coleta e exposição apenas do necessário por papel (schemas) |
| Dados fictícios | Todos os titulares são fictícios (`seed.py`) - sem dado pessoal real |
| Segurança | Argon2id, TLS, autorização, hash+assinatura de integridade, logs |
| Transparência | Documentado que há **decisão automatizada** (IA) sobre currículos |
| Responsabilização | `security_logs` fornece trilha de auditoria |
| Revisão humana | Recomendação explícita de revisão humana da análise de IA (art. sobre decisão automatizada) |

**Base para tratamento (didática):** por serem dados fictícios, não há titular real; o sistema é **modelado como se** tratasse dados pessoais reais para exercitar os controles.

---

## 11. Anonimização, pseudonimização e mascaramento

O edital pede demonstrar **uma** técnica de proteção quando dados são usados em testes/análises. A aplicação demonstra as três, com distinção conceitual correta:

| Técnica | Definição | Implementação | Reversível? |
|---------|-----------|---------------|-------------|
| **Mascaramento** | Ocultar parte do dado na exibição | `mask_cpf/email/phone/name` | Não recupera o original a partir da máscara |
| **Pseudonimização** | Substituir identificador por referência, mantendo ligação controlada | UUID como chave de recurso em vez de expor identidade direta | Sim, com dado adicional (mapeamento no banco) |
| **Anonimização** | Remover ligação a titular de forma irreversível | Análise de IA pode operar sobre texto sem PII direta; logs sem PII | Idealmente irreversível |

**Aplicação em teste/IA:** ao enviar texto do currículo ao pipeline de IA, a superfície de PII é reduzida e o conteúdo é tratado como **dado não confiável** (ver Fase 4). Recomendação futura: cifra simétrica de CPF em repouso (AES-256-GCM) para elevar a proteção do dado sensível além do mascaramento de exibição.

---

## 12. Ligação com a tríade CIA

| Princípio | Controles criptográficos correspondentes |
|-----------|------------------------------------------|
| **Confidencialidade** | Argon2id (senha), TLS (trânsito), autorização + mascaramento (PII) |
| **Integridade** | SHA-256 (arquivo) + endpoint de verificação + validação de conteúdo no upload (magic bytes) |
| **Disponibilidade** | Limite de tamanho de upload, timeout da IA, healthcheck |

---

## 13. Resumo executivo (para o relatório)

> A estratégia criptográfica da SecureRecruit associa cada mecanismo a uma propriedade e a uma ameaça específicas: Argon2id protege senhas contra força bruta offline; TLS protege dados em trânsito; SHA-256 (com endpoint de verificação) detecta adulteração de currículos; HMAC-SHA256 (HS256) assina o token de sessão porque emissor e verificador são o mesmo serviço. A criptografia assimétrica e a assinatura digital ficam documentadas onde se aplicariam (autenticidade de origem do currículo, via Ed25519) e como recomendação futura - o edital pede justificar onde utilizar, e o escopo mínimo de integridade já é atendido pelo hash. Dados sensíveis são protegidos por autorização, minimização e mascaramento (aplicado nas respostas de admin), com cifra simétrica em repouso indicada como evolução. As decisões são justificadas por trade-offs técnicos, não por preferência genérica, e alinhadas à LGPD (finalidade, minimização, transparência sobre decisão automatizada e trilha de auditoria).

---

## 14. Checklist Fase 5

- [x] Criptografia simétrica - onde e por quê (HS256/HMAC; cifra em repouso como evolução)
- [x] Criptografia assimétrica - onde se aplicaria e por que HS256 no JWT (justificativa; não implementada)
- [x] Funções hash - SHA-256 (integridade) vs Argon2id (senha), com distinção
- [x] Proteção de senhas - Argon2id
- [x] Proteção de dados sensíveis - autorização + mascaramento (aplicado no admin) + minimização
- [x] Proteção de dados em trânsito - TLS/HTTPS + CORS
- [x] Assinatura digital - onde se aplicaria (Ed25519 sobre o hash); recomendação futura
- [x] Gerenciamento de chaves - env vars, separação por finalidade, rotação, limitações
- [x] LGPD - finalidade, minimização, transparência, responsabilização, revisão humana
- [x] Anonimização/pseudonimização/mascaramento - três técnicas distinguidas
- [ ] Revisão humana da equipe

---

> **Estado de implementação (para não confundir a banca):**
> - **Implementado e em uso hoje:** Argon2id (senhas), SHA-256 + endpoint de verificação de integridade (currículos), HMAC-SHA256/HS256 (JWT), TLS/HTTPS (trânsito), **mascaramento aplicado nas respostas de admin** (correção R5).
> - **Justificado, não implementado (recomendação futura):** criptografia assimétrica / assinatura digital Ed25519 do hash do currículo; cifra simétrica de PII em repouso (AES-256-GCM).
>
> O edital exige **justificar tecnicamente onde utilizar** cada conceito - não implementar todos. As seções 3 e 7 cumprem isso para a assimétrica/assinatura, deixando claro o porquê da não adoção nesta versão.
