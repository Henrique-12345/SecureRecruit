"""Unit tests for Crypto Lab Phase 4 (controlled attacks)."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.enums import CryptoAlgorithm, UserRole
from app.services.crypto import custom_cipher
from app.services.crypto.attacks import brute_force, differential, statistical
from app.services.crypto.key_service import derive_key
from tests.conftest import auth_header, create_user


def test_truncated_brute_force_recovers_suffix():
    derived = derive_key(algorithm=CryptoAlgorithm.CUSTOM_SPN.value)
    plaintext = b"attack-lab-plaintext!!"
    ciphertext = custom_cipher.encrypt(plaintext, derived.key)
    result = brute_force.run_truncated_brute_force(
        plaintext=plaintext,
        ciphertext=ciphertext,
        full_key=derived.key,
        searchable_bits=10,
        max_attempts=2**10,
    )
    assert result.found is True
    score, label = brute_force.effectiveness_from_bf(result)
    assert score > 0.5
    assert "eficaz" in label


def test_differential_and_statistical_unit():
    key = derive_key(algorithm=CryptoAlgorithm.CUSTOM_SPN.value).key
    pt = b"AAAAAAAAAAAAAAA!"
    diff = differential.run_differential(plaintext=pt, key=key)
    assert 0.0 <= diff.avalanche_score <= 1.0
    score, _ = differential.effectiveness_from_differential(diff)
    assert 0.0 <= score <= 1.0

    ct = custom_cipher.encrypt(pt * 4, key)
    stat = statistical.run_statistical(ct)
    assert "entropy_bits" in stat.report
    s2, _ = statistical.effectiveness_from_statistical(stat)
    assert 0.0 <= s2 <= 1.0


def test_attack_endpoints_admin(client: TestClient, db: Session):
    candidate = create_user(db, email="cand.atk@example.com", role=UserRole.CANDIDATE.value)
    admin = create_user(db, email="admin.atk@example.com", role=UserRole.ADMIN.value)
    cand_h = auth_header(client, candidate.email)
    admin_h = auth_header(client, admin.email)

    denied = client.post(
        "/api/v1/crypto/attacks/differential",
        headers=cand_h,
        json={"plaintext": "hello differential"},
    )
    assert denied.status_code == 403

    diff = client.post(
        "/api/v1/crypto/attacks/differential",
        headers=admin_h,
        json={"plaintext": "hello differential attack!!"},
    )
    assert diff.status_code == 200, diff.text
    body = diff.json()
    assert body["attack_type"] == "differential"
    assert body["effectiveness_score"] is not None
    assert body["metrics"]["avalanche_score"] is not None

    bf = client.post(
        "/api/v1/crypto/attacks/brute-force",
        headers=admin_h,
        json={"plaintext": "bf lab", "searchable_bits": 8},
    )
    assert bf.status_code == 200, bf.text
    assert bf.json()["attack_type"] == "brute_force"
    assert bf.json()["metrics"]["found"] is True

    st = client.post(
        "/api/v1/crypto/attacks/statistical",
        headers=admin_h,
        json={"plaintext": "statistical sample payload for entropy"},
    )
    assert st.status_code == 200, st.text
    assert st.json()["attack_type"] == "statistical"
    assert "entropy_bits" in st.json()["metrics"]

    listing = client.get("/api/v1/crypto/attacks/experiments", headers=admin_h)
    assert listing.status_code == 200
    assert len(listing.json()) >= 3

    detail = client.get(
        f"/api/v1/crypto/attacks/experiments/{bf.json()['id']}", headers=admin_h
    )
    assert detail.status_code == 200
    assert detail.json()["id"] == bf.json()["id"]
