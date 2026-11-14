"""Phase 10 hardening: lab disable flag and size guards."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import UserRole
from app.services.crypto.guards import clamp_searchable_bits, enforce_plaintext_size
from app.core.exceptions import AppError
from tests.conftest import auth_header, create_user
import pytest


def test_plaintext_size_guard(monkeypatch):
    monkeypatch.setattr(settings, "CRYPTO_MAX_PLAINTEXT_BYTES", 10)
    with pytest.raises(AppError):
        enforce_plaintext_size("x" * 11)


def test_searchable_bits_clamp(monkeypatch):
    monkeypatch.setattr(settings, "CRYPTO_LAB_MAX_SEARCHABLE_BITS", 12)
    assert clamp_searchable_bits(8) == 8
    with pytest.raises(AppError):
        clamp_searchable_bits(13)


def test_crypto_lab_disabled_returns_403(client: TestClient, db: Session, monkeypatch):
    monkeypatch.setattr(settings, "CRYPTO_LAB_ENABLED", False)
    admin = create_user(db, email="admin.disabled@example.com", role=UserRole.ADMIN.value)
    headers = auth_header(client, admin.email)
    resp = client.post(
        "/api/v1/crypto/encrypt",
        headers=headers,
        json={"algorithm": "custom_spn", "plaintext": "hello"},
    )
    assert resp.status_code == 403
