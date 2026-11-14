"""Unit tests for Crypto Lab Phase 3 (LSB PNG steganography)."""

from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy.orm import Session

from app.core.enums import UserRole
from app.services.stego import lsb_png
from tests.conftest import auth_header, create_user


def _make_png_bytes(width: int = 64, height: int = 64, color=(40, 80, 120)) -> bytes:
    image = Image.new("RGB", (width, height), color=color)
    buf = BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def test_lsb_roundtrip_unit():
    cover = _make_png_bytes()
    payload = b"encrypted-looking-bytes-0123456789"
    stego, capacity, used = lsb_png.embed_payload(cover, payload)
    assert capacity > used
    assert lsb_png.extract_payload(stego) == payload


def test_stego_embed_extract_api(client: TestClient, db: Session, tmp_path, monkeypatch):
    monkeypatch.setenv("STEGO_DIRECTORY", str(tmp_path / "stego"))
    # settings is cached — override attribute used by service
    from app.core.config import settings

    monkeypatch.setattr(settings, "STEGO_DIRECTORY", str(tmp_path / "stego"))

    candidate = create_user(db, email="cand.stego@example.com", role=UserRole.CANDIDATE.value)
    admin = create_user(db, email="admin.stego@example.com", role=UserRole.ADMIN.value)
    cand_h = auth_header(client, candidate.email)
    admin_h = auth_header(client, admin.email)

    cover = _make_png_bytes(96, 96)
    denied = client.post(
        "/api/v1/stego/embed",
        headers=cand_h,
        files={"cover": ("cover.png", cover, "image/png")},
        data={"plaintext": "secret message", "algorithm": "custom_spn"},
    )
    assert denied.status_code == 403

    embed = client.post(
        "/api/v1/stego/embed",
        headers=admin_h,
        files={"cover": ("cover.png", cover, "image/png")},
        data={"plaintext": "mensagem oculta SecureRecruit", "algorithm": "custom_spn"},
    )
    assert embed.status_code == 201, embed.text
    artifact = embed.json()["artifact"]
    artifact_id = artifact["id"]
    assert artifact["payload_bits"] > 0
    assert artifact["capacity_bits"] >= artifact["payload_bits"]

    listing = client.get("/api/v1/stego/artifacts", headers=admin_h)
    assert listing.status_code == 200
    assert any(a["id"] == artifact_id for a in listing.json())

    download = client.get(f"/api/v1/stego/artifacts/{artifact_id}/download", headers=admin_h)
    assert download.status_code == 200
    assert download.content.startswith(b"\x89PNG")

    extract = client.post(
        "/api/v1/stego/extract",
        headers=admin_h,
        data={"artifact_id": artifact_id},
    )
    assert extract.status_code == 200, extract.text
    assert extract.json()["plaintext"] == "mensagem oculta SecureRecruit"

    # Also extract from uploaded stego bytes with explicit key from payload op
    detail = client.get(f"/api/v1/stego/artifacts/{artifact_id}", headers=admin_h)
    assert detail.status_code == 200
    op_id = detail.json()["payload_operation_id"]
    op = client.get(f"/api/v1/crypto/operations/{op_id}", headers=admin_h)
    assert op.status_code == 200
    key_id = op.json()["key_material_id"]

    extract_file = client.post(
        "/api/v1/stego/extract",
        headers=admin_h,
        files={"stego": ("stego.png", download.content, "image/png")},
        data={"algorithm": "custom_spn", "key_id": key_id},
    )
    assert extract_file.status_code == 200, extract_file.text
    assert extract_file.json()["plaintext"] == "mensagem oculta SecureRecruit"
