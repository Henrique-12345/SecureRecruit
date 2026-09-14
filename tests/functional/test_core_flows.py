from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from tests.conftest import auth_header, create_user


def test_register_and_login(client: TestClient):
    register = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Novo Candidato",
            "email": "novo.candidato@example.com",
            "password": "Demo@1234",
            "role": "candidate",
        },
    )
    assert register.status_code == 201
    assert "access_token" in register.json()

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "novo.candidato@example.com", "password": "Demo@1234"},
    )
    assert login.status_code == 200
    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "novo.candidato@example.com"


def test_job_create_and_apply(
    client: TestClient, db: Session, sample_docx_bytes: bytes
):
    recruiter = create_user(
        db, email="rec.test@example.com", role=UserRole.RECRUITER.value, name="Rec"
    )
    candidate = create_user(
        db, email="cand.test@example.com", role=UserRole.CANDIDATE.value, name="Cand"
    )

    rec_headers = auth_header(client, recruiter.email)
    job = client.post(
        "/api/v1/jobs",
        headers=rec_headers,
        json={
            "title": "Backend Python",
            "description": "Desenvolver APIs com FastAPI e PostgreSQL.",
            "requirements": "Python, FastAPI, PostgreSQL, Docker",
            "location": "Recife",
            "employment_type": "full_time",
            "salary_range": "R$ 7000",
        },
    )
    assert job.status_code == 201
    job_id = job.json()["id"]

    cand_headers = auth_header(client, candidate.email)
    upload = client.post(
        "/api/v1/resumes",
        headers=cand_headers,
        files={
            "file": (
                "cv.docx",
                sample_docx_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert upload.status_code == 201
    resume_id = upload.json()["id"]
    assert len(upload.json()["sha256_hash"]) == 64

    application = client.post(
        f"/api/v1/jobs/{job_id}/applications",
        headers=cand_headers,
        json={"resume_id": resume_id},
    )
    assert application.status_code == 201

    ai = client.post(
        "/api/v1/ai/match-resume-job",
        headers=cand_headers,
        json={"resume_id": resume_id, "job_id": job_id},
    )
    assert ai.status_code == 201
    assert ai.json()["result"]["summary"]


def test_authorization_admin_only(client: TestClient, db: Session):
    candidate = create_user(
        db, email="cand.authz@example.com", role=UserRole.CANDIDATE.value
    )
    headers = auth_header(client, candidate.email)
    response = client.get("/api/v1/admin/users", headers=headers)
    assert response.status_code == 403


def test_admin_can_list_users(client: TestClient, db: Session):
    admin = create_user(db, email="admin.test@example.com", role=UserRole.ADMIN.value)
    headers = auth_header(client, admin.email)
    response = client.get("/api/v1/admin/users", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
