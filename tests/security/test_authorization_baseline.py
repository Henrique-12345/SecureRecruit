from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from tests.conftest import auth_header, create_user


def test_candidate_cannot_access_admin_logs(client: TestClient, db: Session):
    candidate = create_user(
        db, email="cand.sec@example.com", role=UserRole.CANDIDATE.value
    )
    headers = auth_header(client, candidate.email)
    response = client.get("/api/v1/logs", headers=headers)
    assert response.status_code == 403


def test_recruiter_cannot_access_other_candidate_without_application(
    client: TestClient, db: Session
):
    recruiter = create_user(
        db, email="rec.sec@example.com", role=UserRole.RECRUITER.value
    )
    candidate = create_user(
        db, email="cand.sec2@example.com", role=UserRole.CANDIDATE.value
    )
    headers = auth_header(client, recruiter.email)
    response = client.get(f"/api/v1/candidates/{candidate.id}", headers=headers)
    assert response.status_code == 403
