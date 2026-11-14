# Unidade 2 Fase 2 — Criptografia simétrica

## Objetivo

Implementar cifra didática (Custom SPN) + AES-256-GCM com chave dinâmica e endpoints admin.

## Checklist

- [x] `key_service.py` — PBKDF2-HMAC-SHA256 + fingerprint
- [x] `custom_cipher.py` — S-box + P-box + XOR + blocos 16B + 8 rodadas + PKCS7
- [x] `aes_service.py` — AES-256-GCM
- [x] `metrics.py` — avalanche, entropia, histograma/χ²
- [x] `crypto_lab_service.py` — orquestração + persistência + auditoria
- [x] Schemas Pydantic (`schemas/crypto.py`)
- [x] Router `/api/v1/crypto/*` (admin only)
- [x] Testes `tests/security/test_crypto_lab.py`
- [ ] Push da branch

## Endpoints

| Método | Path | Auth |
|--------|------|------|
| POST | `/api/v1/crypto/keys/generate` | admin |
| POST | `/api/v1/crypto/encrypt` | admin |
| POST | `/api/v1/crypto/decrypt` | admin |
| GET | `/api/v1/crypto/operations` | admin |
| GET | `/api/v1/crypto/operations/{id}` | admin |
| POST | `/api/v1/crypto/metrics/avalanche` | admin |
| POST | `/api/v1/crypto/metrics/statistical` | admin |

## Critérios de aceite

1. Round-trip texto com SPN e AES-GCM
2. Chaves distintas → ciphertext distinto (SPN)
3. Operações registradas em `crypto_operations` (sem plaintext/chave em claro nos logs)
4. Candidato recebe 403
