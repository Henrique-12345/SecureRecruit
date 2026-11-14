"""Unit tests for Crypto Lab Phase 5 (analytics / volume)."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from tests.conftest import auth_header, create_user


def test_analytics_seed_and_summary(client: TestClient, db: Session):
    candidate = create_user(db, email="cand.analytics@example.com", role=UserRole.CANDIDATE.value)
    admin = create_user(db, email="admin.analytics@example.com", role=UserRole.ADMIN.value)
    cand_h = auth_header(client, candidate.email)
    admin_h = auth_header(client, admin.email)

    denied = client.get("/api/v1/analytics/events/summary", headers=cand_h)
    assert denied.status_code == 403

    seed = client.post(
        "/api/v1/analytics/seed-load",
        headers=admin_h,
        json={
            "crypto_events": 120,
            "auth_failures": 40,
            "attack_events": 15,
            "hours_span": 24,
        },
    )
    assert seed.status_code == 200, seed.text
    assert seed.json()["total"] == 175

    summary = client.get(
        "/api/v1/analytics/events/summary?hours=48", headers=admin_h
    )
    assert summary.status_code == 200, summary.text
    totals = summary.json()["totals"]
    assert totals["crypto_operations"] >= 120
    assert totals["auth_failures"] >= 40
    assert totals["attack_experiments"] >= 15
    assert totals["events_combined"] >= 175

    ts = client.get(
        "/api/v1/analytics/events/timeseries?hours=48&bucket=hour",
        headers=admin_h,
    )
    assert ts.status_code == 200
    assert "crypto_operations" in ts.json()

    auth = client.get(
        "/api/v1/analytics/auth/failures?hours=48&burst_threshold=5",
        headers=admin_h,
    )
    assert auth.status_code == 200
    assert auth.json()["total_failures"] >= 40

    crypto = client.get("/api/v1/analytics/crypto/failures?hours=48", headers=admin_h)
    assert crypto.status_code == 200
    assert crypto.json()["total_operations"] >= 120
