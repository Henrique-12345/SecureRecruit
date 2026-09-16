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


def test_candidate_cannot_access_recruiter_me_endpoints(client: TestClient, db: Session):
    candidate = create_user(
        db, email="cand.recruiter-endpoint@example.com", role=UserRole.CANDIDATE.value
    )
    headers = auth_header(client, candidate.email)
    assert client.get("/api/v1/recruiters/me", headers=headers).status_code == 403
    assert client.get("/api/v1/recruiters/me/jobs", headers=headers).status_code == 403


def test_fake_docx_upload_rejected(client: TestClient, db: Session):
    candidate = create_user(
        db, email="cand.upload@example.com", role=UserRole.CANDIDATE.value
    )
    headers = auth_header(client, candidate.email)
    response = client.post(
        "/api/v1/resumes",
        headers=headers,
        files={
            "file": (
                "cv_falso.docx",
                b"ARQUIVO TEXTO RENOMEADO PARA DOCX",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert response.status_code == 400
