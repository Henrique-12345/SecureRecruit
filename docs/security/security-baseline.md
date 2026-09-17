# Security Baseline - SecureRecruit

Documento de baseline para a **primeira versão funcional**. Não descreve exploits.

## Controles implementados

- Hash de senha com Argon2id
- Autenticação JWT
- Autorização por papel no backend
- Validação de entrada (Pydantic)
- ORM (SQLAlchemy) em vez de SQL concatenado
- Controle de upload (MIME, extensão, tamanho)
- Nome interno aleatório para arquivos
- SHA-256 e endpoint de verificação de integridade
- Logs de segurança/auditoria
- CORS configurável
- Secrets via variáveis de ambiente
- Pseudonimização utilitária (`mask_cpf`, `mask_email`, `mask_phone`)
- Separação explícita de prompt de IA vs. dados de currículo

## Superfícies naturais para análise futura

Autenticação, autorização/IDOR, upload/download, dados pessoais, API REST, JWT, IA/prompt injection, logs, configuração e integridade de arquivos.

## Fora de escopo nesta fase

- Exploração ofensiva automatizada
- Pentest
- Correção antecipada de todos os cenários possíveis
- Hardening extremo que inviabilize demonstrações acadêmicas posteriores
