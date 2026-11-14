# Unidade 2 Fase 3 — Esteganografia LSB (PNG)

## Objetivo

Ocultar payload **já cifrado** em imagem PNG via LSB; recuperar e decifrar.

## Checklist

- [x] `lsb_png.py` — embed/extract com cabeçalho `SR1\\0` + length
- [x] `stego_lab_service.py` — cifra → embed; extract → decifra
- [x] Storage em `STEGO_DIRECTORY` (cover + stego)
- [x] Schemas + router `/api/v1/stego/*` (admin)
- [x] Dependência `Pillow`
- [x] Testes `tests/security/test_stego_lab.py`
- [ ] Push da branch

## Endpoints

| Método | Path | Auth |
|--------|------|------|
| POST | `/api/v1/stego/embed` | admin (multipart: cover + plaintext) |
| POST | `/api/v1/stego/extract` | admin (arquivo ou `artifact_id`) |
| GET | `/api/v1/stego/artifacts` | admin |
| GET | `/api/v1/stego/artifacts/{id}` | admin |
| GET | `/api/v1/stego/artifacts/{id}/download` | admin |

## Critérios de aceite

1. embed → extract recupera o plaintext
2. `StegoArtifact` + `CryptoOperation` (encrypt + stego_embed/extract) gravados
3. Candidato recebe 403
