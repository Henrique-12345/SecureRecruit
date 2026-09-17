from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from tests.conftest import auth_header, create_user


CPF = "123.456.789-00"
PHONE = "(81) 98765-4321"


def _create_candidate_with_pii(db: Session, email: str):
    user = create_user(db, email=email, role=UserRole.CANDIDATE.value)
    user.cpf = CPF
    user.phone = PHONE
    user.birth_date = date(1995, 7, 14)
    db.commit()
    db.refresh(user)
    return user


def _assert_masked(body: dict) -> None:
    assert body["cpf"] != CPF
    assert "***" in body["cpf"]
    assert body["cpf"].endswith("00")
    assert body["phone"] != PHONE
    assert body["phone"].endswith("4321")
    assert "98765" not in body["phone"]
    assert "birth_date" not in body
    assert body["birth_year"] == 1995


def test_admin_user_list_masks_pii(client: TestClient, db: Session):
    admin = create_user(db, email="admin.pii@example.com", role=UserRole.ADMIN.value)
    candidate = _create_candidate_with_pii(db, "cand.pii@example.com")
    headers = auth_header(client, admin.email)

    response = client.get("/api/v1/admin/users", headers=headers)
    assert response.status_code == 200
    assert CPF not in response.text
    assert PHONE not in response.text

    body = next(u for u in response.json() if u["id"] == str(candidate.id))
    _assert_masked(body)


def test_admin_user_detail_masks_pii(client: TestClient, db: Session):
    admin = create_user(db, email="admin.pii2@example.com", role=UserRole.ADMIN.value)
    candidate = _create_candidate_with_pii(db, "cand.pii2@example.com")
    headers = auth_header(client, admin.email)

    response = client.get(f"/api/v1/admin/users/{candidate.id}", headers=headers)
    assert response.status_code == 200
    _assert_masked(response.json())


def test_owner_still_sees_own_pii_in_clear(client: TestClient, db: Session):
    candidate = _create_candidate_with_pii(db, "cand.pii3@example.com")
    headers = auth_header(client, candidate.email)

    for path in ("/api/v1/users/me", "/api/v1/auth/me"):
        body = client.get(path, headers=headers).json()
        assert body["cpf"] == CPF
        assert body["phone"] == PHONE
        assert body["birth_date"] == "1995-07-14"
