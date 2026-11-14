# Unidade 2 Fase 1 — Modelo de dados

## Entidades

1. **CryptoKeyMaterial** — metadados/fingerprint de chave (sem chave crua)
2. **CryptoOperation** — encrypt/decrypt/stego/métricas
3. **StegoArtifact** — imagens capa/estego
4. **AttackExperiment** — força bruta / diferencial / estatístico
5. **AnomalyEvent** — anomalias detectadas pela IA/regras

## Migration

`backend/alembic/versions/002_crypto_lab_unit2.py`
