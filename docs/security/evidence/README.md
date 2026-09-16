# Evidências — SecureAI Lab / SecureRecruit

Pasta para organizar prints, logs e artefatos do ciclo:

**Análise → Exploração → Correção → Reteste → Apresentação**

## Estrutura

| Pasta | Conteúdo |
|-------|----------|
| `00-ambiente/` | Health, frontend, logins dos 3 papéis, URLs, banco (opcional) |
| `01-threat-model/` | Diagramas, matriz de riscos, listas de ativos/ameaças |
| `02-exploracao/` | Evidências de exploração (request/response, impacto) |
| `03-correcao-reteste/` | Antes/depois do patch e reteste bloqueado |
| `04-ia/` | Prompt injection, saída da IA, mitigação |
| `05-cripto-lgpd/` | Hash/integridade, mascaramento, prints de proteção de dados |
| `06-apresentacao/` | Slides, roteiro, materiais da demo oral |

## Regras

- Preferir PNG/JPG com nomes claros (`login-candidate.png`)
- Não versionar segredos (senhas de banco, JWT secret, connection strings)
- Mascarar dados sensíveis se aparecerem em prints
- Pode incluir a URL na barra de endereço do navegador

## Checklist Fase 0

Ver: [`../fase-0-checklist.md`](../fase-0-checklist.md)
