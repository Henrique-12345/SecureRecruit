"""Unit tests for Crypto Lab Phase 6 (anomaly detection)."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from tests.conftest import auth_header, create_user


def test_auth_burst_anomaly_detection(client: TestClient, db: Session):
    candidate = create_user(db, email="cand.anom@example.com", role=UserRole.CANDIDATE.value)
    admin = create_user(db, email="admin.anom@example.com", role=UserRole.ADMIN.value)
    cand_h = auth_header(client, candidate.email)
    admin_h = auth_header(client, admin.email)

    denied = client.post("/api/v1/anomalies/run", headers=cand_h, json={})
    assert denied.status_code == 403

    # Seed enough login failures to trip auth_burst
    seed = client.post(
        "/api/v1/analytics/seed-load",
        headers=admin_h,
        json={
            "crypto_events": 30,
            "auth_failures": 55,
            "attack_events": 5,
            "hours_span": 6,
        },
    )
    assert seed.status_code == 200, seed.text

    run = client.post(
        "/api/v1/anomalies/run",
        headers=admin_h,
        json={"hours": 24, "auth_burst_threshold": 20},
    )
    assert run.status_code == 200, run.text
    body = run.json()
    assert body["created_count"] >= 1
    types = {a["anomaly_type"] for a in body["anomalies"]}
    assert "auth_burst" in types

    listing = client.get("/api/v1/anomalies?resolved=false", headers=admin_h)
    assert listing.status_code == 200
    assert any(a["anomaly_type"] == "auth_burst" for a in listing.json())

    anomaly_id = next(a["id"] for a in body["anomalies"] if a["anomaly_type"] == "auth_burst")
    detail = client.get(f"/api/v1/anomalies/{anomaly_id}", headers=admin_h)
    assert detail.status_code == 200
    assert detail.json()["evidence"]["total_failures"] >= 20

    resolved = client.patch(f"/api/v1/anomalies/{anomaly_id}/resolve", headers=admin_h)
    assert resolved.status_code == 200
    assert resolved.json()["anomaly"]["resolved"] is True

    # Second run should not recreate same unresolved burst (already resolved → can recreate)
    run2 = client.post(
        "/api/v1/anomalies/run",
        headers=admin_h,
        json={"hours": 24, "auth_burst_threshold": 20},
    )
    assert run2.status_code == 200
