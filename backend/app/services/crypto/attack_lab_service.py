"""Orchestration for controlled crypto attacks (Unit 2 Phase 4)."""

from __future__ import annotations

import base64
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import (
    AttackType,
    CryptoAlgorithm,
    CryptoInputKind,
    CryptoOperationType,
    SecurityEventType,
)
from app.core.exceptions import AppError, NotFoundError
from app.models.attack_experiment import AttackExperiment
from app.models.crypto_operation import CryptoOperation
from app.models.user import User
from app.services.audit_service import AuditService
from app.services.crypto import custom_cipher
from app.services.crypto.attacks import brute_force, differential, statistical
from app.services.crypto.crypto_lab_service import CryptoLabService
from app.services.crypto.guards import (
    clamp_searchable_bits,
    ensure_crypto_lab_enabled,
    enforce_plaintext_size,
)


class AttackLabService:
    def __init__(self, db: Session):
        self.db = db

    def _ensure_enabled(self) -> None:
        ensure_crypto_lab_enabled()

    def brute_force(
        self,
        *,
        user: User,
        plaintext: str,
        searchable_bits: int = 12,
        key_id: UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AttackExperiment:
        self._ensure_enabled()
        searchable_bits = clamp_searchable_bits(searchable_bits)
        enforce_plaintext_size(plaintext, label="plaintext")
        algorithm = CryptoAlgorithm.CUSTOM_SPN.value
        crypto = CryptoLabService(self.db)
        material, key_bytes = crypto.resolve_key(
            user=user, algorithm=algorithm, key_id=key_id
        )
        pt = plaintext.encode("utf-8")
        ct = custom_cipher.encrypt(pt, key_bytes)

        result = brute_force.run_truncated_brute_force(
            plaintext=pt,
            ciphertext=ct,
            full_key=key_bytes,
            searchable_bits=searchable_bits,
            max_attempts=settings.CRYPTO_LAB_MAX_ATTACK_ATTEMPTS,
        )
        score, label = brute_force.effectiveness_from_bf(result)
        metrics = {
            "found": result.found,
            "attempts": result.attempts,
            "max_attempts": result.max_attempts,
            "keyspace_size": result.keyspace_size,
            "elapsed_ms": result.elapsed_ms,
            "recovered_key_suffix_hex": result.recovered_key_suffix_hex,
            "estimated_full_keyspace_years": result.estimated_full_keyspace_years,
            "label": label,
            "notes": result.notes,
        }
        return self._persist(
            user=user,
            attack_type=AttackType.BRUTE_FORCE.value,
            algorithm=algorithm,
            parameters={
                "searchable_bits": searchable_bits,
                "key_id": str(material.id),
                "plaintext_len": len(pt),
            },
            result_summary=label,
            metrics=metrics,
            effectiveness_score=score,
            operation_type=CryptoOperationType.ATTACK_BRUTE_FORCE.value,
            key_material_id=material.id,
            input_size=len(pt),
            ip_address=ip_address,
            user_agent=user_agent,
        )

    def differential(
        self,
        *,
        user: User,
        plaintext: str,
        key_id: UUID | None = None,
        flip_byte_index: int = 0,
        flip_bit_mask: int = 0x01,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AttackExperiment:
        self._ensure_enabled()
        enforce_plaintext_size(plaintext, label="plaintext")
        algorithm = CryptoAlgorithm.CUSTOM_SPN.value
        crypto = CryptoLabService(self.db)
        material, key_bytes = crypto.resolve_key(
            user=user, algorithm=algorithm, key_id=key_id
        )
        pt = plaintext.encode("utf-8")
        result = differential.run_differential(
            plaintext=pt,
            key=key_bytes,
            flip_byte_index=flip_byte_index,
            flip_bit_mask=flip_bit_mask,
        )
        score, label = differential.effectiveness_from_differential(result)
        metrics = {
            "avalanche_score": round(result.avalanche_score, 6),
            "hamming_bits": result.hamming_bits,
            "flipped_input_bits": result.flipped_input_bits,
            "ciphertext_a_len": result.ciphertext_a_len,
            "ciphertext_b_len": result.ciphertext_b_len,
            "label": label,
            "notes": result.notes,
        }
        return self._persist(
            user=user,
            attack_type=AttackType.DIFFERENTIAL.value,
            algorithm=algorithm,
            parameters={
                "flip_byte_index": flip_byte_index,
                "flip_bit_mask": flip_bit_mask,
                "key_id": str(material.id),
            },
            result_summary=label,
            metrics=metrics,
            effectiveness_score=score,
            operation_type=CryptoOperationType.ATTACK_DIFFERENTIAL.value,
            key_material_id=material.id,
            input_size=len(pt),
            avalanche_score=result.avalanche_score,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    def statistical(
        self,
        *,
        user: User,
        ciphertext_b64: str | None = None,
        plaintext: str | None = None,
        key_id: UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AttackExperiment:
        self._ensure_enabled()
        algorithm = CryptoAlgorithm.CUSTOM_SPN.value
        crypto = CryptoLabService(self.db)

        if ciphertext_b64:
            try:
                ciphertext = base64.b64decode(ciphertext_b64, validate=True)
            except Exception as exc:  # noqa: BLE001
                raise AppError("Invalid base64 ciphertext", status_code=400) from exc
            material_id = key_id
        elif plaintext:
            material, key_bytes = crypto.resolve_key(
                user=user, algorithm=algorithm, key_id=key_id
            )
            ciphertext = custom_cipher.encrypt(plaintext.encode("utf-8"), key_bytes)
            material_id = material.id
        else:
            raise AppError("Provide ciphertext_b64 or plaintext", status_code=400)

        result = statistical.run_statistical(ciphertext)
        score, label = statistical.effectiveness_from_statistical(result)
        metrics = {**result.report, "label": label, "notes": result.notes}
        return self._persist(
            user=user,
            attack_type=AttackType.STATISTICAL.value,
            algorithm=algorithm,
            parameters={
                "ciphertext_len": len(ciphertext),
                "key_id": str(material_id) if material_id else None,
                "from_plaintext": bool(plaintext),
            },
            result_summary=label,
            metrics=metrics,
            effectiveness_score=score,
            operation_type=CryptoOperationType.ATTACK_STATISTICAL.value,
            key_material_id=material_id if isinstance(material_id, UUID) else None,
            input_size=len(ciphertext),
            ip_address=ip_address,
            user_agent=user_agent,
        )

    def list_experiments(self, *, limit: int = 50) -> list[AttackExperiment]:
        self._ensure_enabled()
        return (
            self.db.query(AttackExperiment)
            .order_by(AttackExperiment.created_at.desc())
            .limit(min(limit, 200))
            .all()
        )

    def get_experiment(self, experiment_id: UUID) -> AttackExperiment:
        self._ensure_enabled()
        exp = (
            self.db.query(AttackExperiment)
            .filter(AttackExperiment.id == experiment_id)
            .first()
        )
        if not exp:
            raise NotFoundError("Attack experiment not found")
        return exp

    def _persist(
        self,
        *,
        user: User,
        attack_type: str,
        algorithm: str,
        parameters: dict,
        result_summary: str,
        metrics: dict,
        effectiveness_score: float,
        operation_type: str,
        key_material_id: UUID | None,
        input_size: int,
        avalanche_score: float | None = None,
        ip_address: str | None,
        user_agent: str | None,
    ) -> AttackExperiment:
        experiment = AttackExperiment(
            user_id=user.id,
            attack_type=attack_type,
            algorithm=algorithm,
            parameters=parameters,
            result_summary=result_summary,
            metrics=metrics,
            effectiveness_score=effectiveness_score,
        )
        self.db.add(experiment)
        self.db.flush()

        op = CryptoOperation(
            user_id=user.id,
            key_material_id=key_material_id,
            operation_type=operation_type,
            algorithm=algorithm,
            input_kind=CryptoInputKind.TEXT.value,
            input_size=input_size,
            output_size=0,
            success=True,
            avalanche_score=avalanche_score,
            details={
                "attack_experiment_id": str(experiment.id),
                "effectiveness_score": effectiveness_score,
                "label": result_summary,
            },
        )
        self.db.add(op)
        self.db.commit()
        self.db.refresh(experiment)

        AuditService(self.db).log_event(
            event_type=SecurityEventType.ATTACK,
            action=attack_type,
            success=True,
            user_id=user.id,
            resource="attack_experiment",
            resource_id=experiment.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=f"score={effectiveness_score:.3f} {result_summary}",
        )
        return experiment
