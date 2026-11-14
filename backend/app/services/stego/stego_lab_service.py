"""Steganography lab orchestration: encrypt → LSB embed / extract → decrypt."""

from __future__ import annotations

import base64
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import CryptoAlgorithm, CryptoInputKind, CryptoOperationType, SecurityEventType
from app.core.exceptions import AppError, NotFoundError
from app.models.crypto_operation import CryptoOperation
from app.models.stego_artifact import StegoArtifact
from app.models.user import User
from app.services.audit_service import AuditService
from app.services.crypto.crypto_lab_service import CryptoLabService
from app.services.crypto.guards import (
    ensure_crypto_lab_enabled,
    enforce_cover_size,
    enforce_plaintext_size,
)
from app.services.stego import lsb_png


PNG_MIME = "image/png"


class StegoLabService:
    def __init__(self, db: Session):
        self.db = db
        self.stego_dir = Path(settings.STEGO_DIRECTORY)
        self.stego_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_enabled(self) -> None:
        ensure_crypto_lab_enabled()

    def embed(
        self,
        *,
        user: User,
        cover: UploadFile,
        plaintext: str,
        algorithm: str = CryptoAlgorithm.CUSTOM_SPN.value,
        key_id: uuid.UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> StegoArtifact:
        self._ensure_enabled()
        enforce_plaintext_size(plaintext, label="stego plaintext")
        cover_bytes = self._read_png(cover)

        crypto = CryptoLabService(self.db)
        operation, ciphertext_b64, _fingerprint = crypto.encrypt(
            user=user,
            algorithm=algorithm,
            plaintext=plaintext.encode("utf-8"),
            input_kind=CryptoInputKind.TEXT.value,
            key_id=key_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        ciphertext = base64.b64decode(ciphertext_b64)

        try:
            stego_bytes, capacity_bits, payload_bits = lsb_png.embed_payload(
                cover_bytes, ciphertext
            )
        except ValueError as exc:
            raise AppError(str(exc), status_code=400) from exc

        cover_name = Path(cover.filename or "cover.png").name
        cover_stored = f"{uuid.uuid4().hex}_cover.png"
        stego_stored = f"{uuid.uuid4().hex}_stego.png"
        cover_path = self.stego_dir / cover_stored
        stego_path = self.stego_dir / stego_stored
        cover_path.write_bytes(cover_bytes)
        stego_path.write_bytes(stego_bytes)

        artifact = StegoArtifact(
            user_id=user.id,
            payload_operation_id=operation.id,
            cover_original_filename=cover_name,
            cover_stored_filename=cover_stored,
            cover_file_path=str(cover_path),
            stego_stored_filename=stego_stored,
            stego_file_path=str(stego_path),
            capacity_bits=capacity_bits,
            payload_bits=payload_bits,
        )
        self.db.add(artifact)

        embed_op = CryptoOperation(
            user_id=user.id,
            key_material_id=operation.key_material_id,
            operation_type=CryptoOperationType.STEGO_EMBED.value,
            algorithm=algorithm,
            input_kind=CryptoInputKind.FILE.value,
            input_size=len(cover_bytes),
            output_size=len(stego_bytes),
            success=True,
            details={
                "capacity_bits": capacity_bits,
                "payload_bits": payload_bits,
                "payload_operation_id": str(operation.id),
            },
        )
        self.db.add(embed_op)
        self.db.commit()
        self.db.refresh(artifact)

        AuditService(self.db).log_event(
            event_type=SecurityEventType.STEGO,
            action="stego_embed",
            success=True,
            user_id=user.id,
            resource="stego_artifact",
            resource_id=artifact.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=f"capacity={capacity_bits} payload_bits={payload_bits}",
        )
        return artifact

    def extract(
        self,
        *,
        user: User,
        stego_file: UploadFile | None = None,
        artifact_id: uuid.UUID | None = None,
        algorithm: str | None = None,
        key_id: uuid.UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[StegoArtifact | None, str]:
        self._ensure_enabled()
        artifact: StegoArtifact | None = None

        if artifact_id is not None:
            artifact = (
                self.db.query(StegoArtifact).filter(StegoArtifact.id == artifact_id).first()
            )
            if not artifact:
                raise NotFoundError("Stego artifact not found")
            stego_bytes = Path(artifact.stego_file_path).read_bytes()
            if artifact.payload_operation_id and (algorithm is None or key_id is None):
                op = (
                    self.db.query(CryptoOperation)
                    .filter(CryptoOperation.id == artifact.payload_operation_id)
                    .first()
                )
                if op:
                    algorithm = algorithm or op.algorithm
                    key_id = key_id or op.key_material_id
        elif stego_file is not None:
            stego_bytes = self._read_png(stego_file)
        else:
            raise AppError("Provide stego file or artifact_id", status_code=400)

        if not algorithm or not key_id:
            raise AppError(
                "algorithm and key_id are required when not using a known artifact",
                status_code=400,
            )

        try:
            ciphertext = lsb_png.extract_payload(stego_bytes)
        except ValueError as exc:
            raise AppError(str(exc), status_code=400) from exc

        crypto = CryptoLabService(self.db)
        operation, plaintext = crypto.decrypt(
            user=user,
            algorithm=algorithm,
            ciphertext_b64=base64.b64encode(ciphertext).decode("ascii"),
            key_id=key_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        extract_op = CryptoOperation(
            user_id=user.id,
            key_material_id=operation.key_material_id,
            operation_type=CryptoOperationType.STEGO_EXTRACT.value,
            algorithm=algorithm,
            input_kind=CryptoInputKind.FILE.value,
            input_size=len(stego_bytes),
            output_size=len(plaintext),
            success=True,
            details={"decrypt_operation_id": str(operation.id)},
        )
        self.db.add(extract_op)
        self.db.commit()

        AuditService(self.db).log_event(
            event_type=SecurityEventType.STEGO,
            action="stego_extract",
            success=True,
            user_id=user.id,
            resource="stego_artifact",
            resource_id=artifact.id if artifact else None,
            ip_address=ip_address,
            user_agent=user_agent,
            details=f"plaintext_bytes={len(plaintext)}",
        )
        try:
            text = plaintext.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise AppError("Recovered payload is not valid UTF-8 text", status_code=400) from exc
        return artifact, text

    def list_artifacts(self, *, limit: int = 50) -> list[StegoArtifact]:
        self._ensure_enabled()
        return (
            self.db.query(StegoArtifact)
            .order_by(StegoArtifact.created_at.desc())
            .limit(min(limit, 200))
            .all()
        )

    def get_artifact(self, artifact_id: uuid.UUID) -> StegoArtifact:
        self._ensure_enabled()
        artifact = self.db.query(StegoArtifact).filter(StegoArtifact.id == artifact_id).first()
        if not artifact:
            raise NotFoundError("Stego artifact not found")
        return artifact

    def _read_png(self, file: UploadFile) -> bytes:
        content = file.file.read()
        if not content:
            raise AppError("Empty file", status_code=400)
        enforce_cover_size(content)
        name = (file.filename or "").lower()
        if not name.endswith(".png"):
            raise AppError("Only PNG images are supported", status_code=400)
        if not content.startswith(b"\x89PNG\r\n\x1a\n"):
            raise AppError("File content is not a valid PNG", status_code=400)
        content_type = (file.content_type or "").lower()
        if content_type and content_type not in {PNG_MIME, "application/octet-stream"}:
            raise AppError("MIME type must be image/png", status_code=400)
        return content
