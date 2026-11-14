"""Unit tests for Crypto Lab Phase 2 (SPN + AES-GCM + authz)."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.enums import CryptoAlgorithm, UserRole
from app.services.crypto import aes_service, custom_cipher
from app.services.crypto.key_service import derive_key
from app.services.crypto.metrics import avalanche_score, shannon_entropy
from tests.conftest import auth_header, create_user


def test_custom_spn_roundtrip():
    key = derive_key(algorithm=CryptoAlgorithm.CUSTOM_SPN.value).key
    plaintext = b"SecureRecruit crypto lab roundtrip"
    ciphertext = custom_cipher.encrypt(plaintext, key)
    assert ciphertext != plaintext
    assert custom_cipher.decrypt(ciphertext, key) == plaintext


def test_custom_spn_different_keys_different_ciphertext():
    p = b"same plaintext for both keys!!"
    k1 = derive_key(algorithm=CryptoAlgorithm.CUSTOM_SPN.value).key
    k2 = derive_key(algorithm=CryptoAlgorithm.CUSTOM_SPN.value).key
    assert custom_cipher.encrypt(p, k1) != custom_cipher.encrypt(p, k2)


def test_aes_gcm_roundtrip():
    key = derive_key(algorithm=CryptoAlgorithm.AES_256_GCM.value).key
    plaintext = b"aes-256-gcm lab payload"
    blob = aes_service.encrypt(plaintext, key)
    assert aes_service.decrypt(blob, key) == plaintext


def test_spn_avalanche_nonzero():
    key = derive_key(algorithm=CryptoAlgorithm.CUSTOM_SPN.value).key
    a = b"AAAAAAAAAAAAAAA!"
    b = bytearray(a)
    b[0] ^= 1
    c1 = custom_cipher.encrypt(a, key)
    c2 = custom_cipher.encrypt(bytes(b), key)
    score = avalanche_score(c1, c2)
    assert 0.0 < score <= 1.0
    assert shannon_entropy(c1) > 3.0


def test_crypto_endpoints_admin_only(client: TestClient, db: Session):
    candidate = create_user(db, email="cand.crypto@example.com", role=UserRole.CANDIDATE.value)
    admin = create_user(db, email="admin.crypto@example.com", role=UserRole.ADMIN.value)
    cand_h = auth_header(client, candidate.email)
    admin_h = auth_header(client, admin.email)

    denied = client.post(
        "/api/v1/crypto/encrypt",
        headers=cand_h,
        json={"algorithm": "custom_spn", "plaintext": "hello"},
    )
    assert denied.status_code == 403

    enc = client.post(
        "/api/v1/crypto/encrypt",
        headers=admin_h,
        json={"algorithm": "custom_spn", "plaintext": "hello crypto lab"},
    )
    assert enc.status_code == 200, enc.text
    body = enc.json()
    assert body["ciphertext_b64"]
    assert body["key_id"]

    dec = client.post(
        "/api/v1/crypto/decrypt",
        headers=admin_h,
        json={
            "algorithm": "custom_spn",
            "ciphertext_b64": body["ciphertext_b64"],
            "key_id": body["key_id"],
        },
    )
    assert dec.status_code == 200, dec.text
    assert dec.json()["plaintext"] == "hello crypto lab"

    aes_enc = client.post(
        "/api/v1/crypto/encrypt",
        headers=admin_h,
        json={"algorithm": "aes-256-gcm", "plaintext": "aes payload"},
    )
    assert aes_enc.status_code == 200, aes_enc.text
    aes_body = aes_enc.json()
    aes_dec = client.post(
        "/api/v1/crypto/decrypt",
        headers=admin_h,
        json={
            "algorithm": "aes-256-gcm",
            "ciphertext_b64": aes_body["ciphertext_b64"],
            "key_id": aes_body["key_id"],
        },
    )
    assert aes_dec.status_code == 200
    assert aes_dec.json()["plaintext"] == "aes payload"

    key_resp = client.post(
        "/api/v1/crypto/keys/generate",
        headers=admin_h,
        json={"algorithm": "custom_spn", "label": "lab-key-1"},
    )
    assert key_resp.status_code == 200
    key_id = key_resp.json()["id"]

    enc2 = client.post(
        "/api/v1/crypto/encrypt",
        headers=admin_h,
        json={
            "algorithm": "custom_spn",
            "plaintext": "with handle",
            "key_id": key_id,
        },
    )
    assert enc2.status_code == 200

    av = client.post(
        "/api/v1/crypto/metrics/avalanche",
        headers=admin_h,
        json={"algorithm": "custom_spn", "plaintext": "diffusion demo text!!", "key_id": key_id},
    )
    assert av.status_code == 200
    assert "avalanche_score" in av.json()["report"]

    st = client.post(
        "/api/v1/crypto/metrics/statistical",
        headers=admin_h,
        json={"algorithm": "custom_spn", "ciphertext_b64": enc2.json()["ciphertext_b64"]},
    )
    assert st.status_code == 200
    assert st.json()["report"]["entropy_bits"] > 0

    ops = client.get("/api/v1/crypto/operations", headers=admin_h)
    assert ops.status_code == 200
    assert len(ops.json()) >= 1
