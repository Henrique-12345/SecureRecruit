"""Crypto Lab orchestration: keys, encrypt/decrypt, metrics, audit persistence."""

from __future__ import annotations

import base64
import time
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import (
    CryptoAlgorithm,
    CryptoInputKind,
    CryptoOperationType,
    SecurityEventType,
)
from app.core.exceptions import AppError, ForbiddenError, NotFoundError
from app.models.crypto_key_material import CryptoKeyMaterial
from app.models.crypto_operation import CryptoOperation
from app.models.user import User
from app.services.audit_service import AuditService
from app.services.crypto import aes_service, custom_cipher
from app.services.crypto import metrics as crypto_metrics
from app.services.crypto.key_service import derive_key


class CryptoLabService:
    def __init__(self, db: Session):
        self.db = db

    def _ensure_enabled(self) -> None:
        if not settings.CRYPTO_LAB_ENABLED:
            raise ForbiddenError("Crypto Lab is disabled")

    def generate_key(
        self,
        *,
        owner: User,
        algorithm: str,
        label: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> CryptoKeyMaterial:
        self._ensure_enabled()
        self._validate_algorithm(algorithm)
        derived = derive_key(algorithm=algorithm)
        material = CryptoKeyMaterial(
            owner_id=owner.id,
            key_fingerprint=derived.fingerprint,
            derivation_info=derived.derivation_info(),
            algorithm=algorithm,
            label=label,
            is_active=True,
        )
        self.db.add(material)
        self.db.commit()
        self.db.refresh(material)

        AuditService(self.db).log_event(
            event_type=SecurityEventType.CRYPTO,
            action="key_generated",
            success=True,
            user_id=owner.id,
            resource="crypto_key_material",
            resource_id=material.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=f"algorithm={algorithm} fingerprint={derived.fingerprint[:16]}…",
        )
        return material

    def encrypt(
        self,
        *,
        user: User,
        algorithm: str,
        plaintext: bytes,
        input_kind: str = CryptoInputKind.TEXT.value,
        key_id: UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[CryptoOperation, str, str]:
        """Returns (operation, ciphertext_b64, key_fingerprint)."""
        self._ensure_enabled()
        self._validate_algorithm(algorithm)
        started = time.perf_counter()
        key_material, key_bytes = self._resolve_key(user=user, algorithm=algorithm, key_id=key_id)

        try:
            if algorithm == CryptoAlgorithm.CUSTOM_SPN.value:
                ciphertext = custom_cipher.encrypt(plaintext, key_bytes)
            else:
                ciphertext = aes_service.encrypt(plaintext, key_bytes)
            success = True
            error_code = None
        except Exception as exc:  # noqa: BLE001
            ciphertext = b""
            success = False
            error_code = type(exc).__name__

        duration_ms = int((time.perf_counter() - started) * 1000)
        operation = CryptoOperation(
            user_id=user.id,
            key_material_id=key_material.id if key_material else None,
            operation_type=CryptoOperationType.ENCRYPT.value,
            algorithm=algorithm,
            input_kind=input_kind,
            input_size=len(plaintext),
            output_size=len(ciphertext),
            success=success,
            error_code=error_code,
            duration_ms=duration_ms,
            details={
                "salt_hex": (key_material.derivation_info or {}).get("salt_hex")
                if key_material
                else None,
                "key_fingerprint": key_material.key_fingerprint if key_material else None,
            },
        )
        self.db.add(operation)
        self.db.commit()
        self.db.refresh(operation)

        AuditService(self.db).log_event(
            event_type=SecurityEventType.CRYPTO,
            action="encrypt",
            success=success,
            user_id=user.id,
            resource="crypto_operation",
            resource_id=operation.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=f"algorithm={algorithm} in={len(plaintext)} out={len(ciphertext)}",
        )

        if not success:
            raise AppError("Encryption failed", status_code=400, details=error_code)

        return (
            operation,
            base64.b64encode(ciphertext).decode("ascii"),
            key_material.key_fingerprint if key_material else "",
        )

    def decrypt(
        self,
        *,
        user: User,
        algorithm: str,
        ciphertext_b64: str,
        key_id: UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[CryptoOperation, bytes]:
        self._ensure_enabled()
        self._validate_algorithm(algorithm)
        started = time.perf_counter()
        try:
            ciphertext = base64.b64decode(ciphertext_b64, validate=True)
        except Exception as exc:  # noqa: BLE001
            raise AppError("Invalid base64 ciphertext", status_code=400) from exc

        key_material, key_bytes = self._resolve_key(user=user, algorithm=algorithm, key_id=key_id)
        plaintext = b""
        success = True
        error_code = None
        try:
            if algorithm == CryptoAlgorithm.CUSTOM_SPN.value:
                plaintext = custom_cipher.decrypt(ciphertext, key_bytes)
            else:
                plaintext = aes_service.decrypt(ciphertext, key_bytes)
        except Exception as exc:  # noqa: BLE001
            success = False
            error_code = type(exc).__name__

        duration_ms = int((time.perf_counter() - started) * 1000)
        operation = CryptoOperation(
            user_id=user.id,
            key_material_id=key_material.id if key_material else None,
            operation_type=CryptoOperationType.DECRYPT.value,
            algorithm=algorithm,
            input_kind=CryptoInputKind.TEXT.value,
            input_size=len(ciphertext),
            output_size=len(plaintext),
            success=success,
            error_code=error_code,
            duration_ms=duration_ms,
            details={
                "key_fingerprint": key_material.key_fingerprint if key_material else None,
            },
        )
        self.db.add(operation)
        self.db.commit()
        self.db.refresh(operation)

        AuditService(self.db).log_event(
            event_type=SecurityEventType.CRYPTO,
            action="decrypt",
            success=success,
            user_id=user.id,
            resource="crypto_operation",
            resource_id=operation.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=f"algorithm={algorithm} error={error_code}",
        )

        if not success:
            raise AppError("Decryption failed", status_code=400, details=error_code)
        return operation, plaintext

    def list_operations(self, *, limit: int = 50) -> list[CryptoOperation]:
        self._ensure_enabled()
        return (
            self.db.query(CryptoOperation)
            .order_by(CryptoOperation.created_at.desc())
            .limit(min(limit, 200))
            .all()
        )

    def get_operation(self, operation_id: UUID) -> CryptoOperation:
        self._ensure_enabled()
        op = self.db.query(CryptoOperation).filter(CryptoOperation.id == operation_id).first()
        if not op:
            raise NotFoundError("Crypto operation not found")
        return op

    def avalanche(
        self,
        *,
        user: User,
        algorithm: str,
        plaintext: bytes,
        key_id: UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[CryptoOperation, dict]:
        self._ensure_enabled()
        self._validate_algorithm(algorithm)
        if not plaintext:
            raise AppError("Plaintext required", status_code=400)

        key_material, key_bytes = self._resolve_key(user=user, algorithm=algorithm, key_id=key_id)
        flipped = bytearray(plaintext)
        flipped[0] ^= 0x01
        flipped_bytes = bytes(flipped)

        if algorithm == CryptoAlgorithm.CUSTOM_SPN.value:
            c1 = custom_cipher.encrypt(plaintext, key_bytes)
            c2 = custom_cipher.encrypt(flipped_bytes, key_bytes)
        else:
            # AES-GCM includes random nonce → avalanche not meaningful across nonces;
            # still report bit difference of payloads for lab visibility.
            c1 = aes_service.encrypt(plaintext, key_bytes)
            c2 = aes_service.encrypt(flipped_bytes, key_bytes)

        score = crypto_metrics.avalanche_score(c1, c2)
        report = {
            "avalanche_score": round(score, 6),
            "hamming_bits": crypto_metrics.hamming_distance(c1, c2),
            "cipher_len_a": len(c1),
            "cipher_len_b": len(c2),
            "note": (
                "SPN uses deterministic blocks (diffusion demo). "
                "AES-GCM includes random nonce so score mixes nonce entropy."
                if algorithm == CryptoAlgorithm.AES_256_GCM.value
                else "Ideal diffusion ≈ 0.5"
            ),
        }
        operation = CryptoOperation(
            user_id=user.id,
            key_material_id=key_material.id if key_material else None,
            operation_type=CryptoOperationType.METRIC_AVALANCHE.value,
            algorithm=algorithm,
            input_kind=CryptoInputKind.TEXT.value,
            input_size=len(plaintext),
            output_size=0,
            success=True,
            avalanche_score=score,
            details=report,
        )
        self.db.add(operation)
        self.db.commit()
        self.db.refresh(operation)

        AuditService(self.db).log_event(
            event_type=SecurityEventType.CRYPTO,
            action="metric_avalanche",
            success=True,
            user_id=user.id,
            resource="crypto_operation",
            resource_id=operation.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=f"score={score:.4f}",
        )
        return operation, report

    def statistical(
        self,
        *,
        user: User,
        ciphertext_b64: str,
        algorithm: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[CryptoOperation, dict]:
        self._ensure_enabled()
        try:
            ciphertext = base64.b64decode(ciphertext_b64, validate=True)
        except Exception as exc:  # noqa: BLE001
            raise AppError("Invalid base64 ciphertext", status_code=400) from exc

        report = crypto_metrics.statistical_report(ciphertext)
        operation = CryptoOperation(
            user_id=user.id,
            operation_type=CryptoOperationType.METRIC_STATISTICAL.value,
            algorithm=algorithm,
            input_kind=CryptoInputKind.TEXT.value,
            input_size=len(ciphertext),
            output_size=0,
            success=True,
            details=report,
        )
        self.db.add(operation)
        self.db.commit()
        self.db.refresh(operation)

        AuditService(self.db).log_event(
            event_type=SecurityEventType.CRYPTO,
            action="metric_statistical",
            success=True,
            user_id=user.id,
            resource="crypto_operation",
            resource_id=operation.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=f"entropy={report['entropy_bits']}",
        )
        return operation, report

    def _validate_algorithm(self, algorithm: str) -> None:
        allowed = {a.value for a in CryptoAlgorithm}
        if algorithm not in allowed:
            raise AppError(f"Unsupported algorithm: {algorithm}", status_code=400)

    def _resolve_key(
        self, *, user: User, algorithm: str, key_id: UUID | None
    ) -> tuple[CryptoKeyMaterial, bytes]:
        if key_id is not None:
            material = (
                self.db.query(CryptoKeyMaterial)
                .filter(CryptoKeyMaterial.id == key_id, CryptoKeyMaterial.is_active.is_(True))
                .first()
            )
            if not material:
                raise NotFoundError("Key material not found")
            if material.algorithm != algorithm:
                raise AppError("Key algorithm mismatch", status_code=400)
            info = material.derivation_info or {}
            salt_hex = info.get("salt_hex")
            if not salt_hex:
                raise AppError("Key material missing salt", status_code=400)
            derived = derive_key(
                salt=bytes.fromhex(salt_hex),
                algorithm=algorithm,
                iterations=info.get("iterations"),
            )
            return material, derived.key

        # Ephemeral key material persisted for this operation
        derived = derive_key(algorithm=algorithm)
        material = CryptoKeyMaterial(
            owner_id=user.id,
            key_fingerprint=derived.fingerprint,
            derivation_info=derived.derivation_info(),
            algorithm=algorithm,
            label="ephemeral",
            is_active=True,
        )
        self.db.add(material)
        self.db.flush()
        return material, derived.key
