"""Analytics over Crypto Lab + security events (Unit 2 Phase 5)."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import (
    AttackType,
    CryptoAlgorithm,
    CryptoInputKind,
    CryptoOperationType,
    SecurityEventType,
)
from app.core.exceptions import AppError, ForbiddenError
from app.models.attack_experiment import AttackExperiment
from app.models.crypto_operation import CryptoOperation
from app.models.security_log import SecurityLog
from app.models.stego_artifact import StegoArtifact
from app.models.user import User


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def _ensure_enabled(self) -> None:
        if not settings.CRYPTO_LAB_ENABLED:
            raise ForbiddenError("Crypto Lab is disabled")

    def events_summary(self, *, hours: int = 24) -> dict[str, Any]:
        self._ensure_enabled()
        since = datetime.now(timezone.utc) - timedelta(hours=hours)

        crypto_total = (
            self.db.query(func.count(CryptoOperation.id))
            .filter(CryptoOperation.created_at >= since)
            .scalar()
            or 0
        )
        crypto_by_type = dict(
            self.db.query(CryptoOperation.operation_type, func.count(CryptoOperation.id))
            .filter(CryptoOperation.created_at >= since)
            .group_by(CryptoOperation.operation_type)
            .all()
        )
        crypto_fail = (
            self.db.query(func.count(CryptoOperation.id))
            .filter(
                CryptoOperation.created_at >= since,
                CryptoOperation.success.is_(False),
            )
            .scalar()
            or 0
        )
        auth_fail = (
            self.db.query(func.count(SecurityLog.id))
            .filter(
                SecurityLog.timestamp >= since,
                SecurityLog.event_type == SecurityEventType.AUTH.value,
                SecurityLog.success.is_(False),
            )
            .scalar()
            or 0
        )
        attacks = (
            self.db.query(func.count(AttackExperiment.id))
            .filter(AttackExperiment.created_at >= since)
            .scalar()
            or 0
        )
        stego = (
            self.db.query(func.count(StegoArtifact.id))
            .filter(StegoArtifact.created_at >= since)
            .scalar()
            or 0
        )
        security_logs = (
            self.db.query(func.count(SecurityLog.id))
            .filter(SecurityLog.timestamp >= since)
            .scalar()
            or 0
        )

        return {
            "window_hours": hours,
            "since": since.isoformat(),
            "totals": {
                "crypto_operations": crypto_total,
                "crypto_failures": crypto_fail,
                "security_logs": security_logs,
                "auth_failures": auth_fail,
                "attack_experiments": attacks,
                "stego_artifacts": stego,
                "events_combined": crypto_total + security_logs + attacks + stego,
            },
            "crypto_by_operation_type": crypto_by_type,
        }

    def events_timeseries(self, *, hours: int = 24, bucket: str = "hour") -> dict[str, Any]:
        self._ensure_enabled()
        if bucket not in {"hour", "day"}:
            raise AppError("bucket must be 'hour' or 'day'", status_code=400)
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        trunc = "hour" if bucket == "hour" else "day"

        crypto_rows = (
            self.db.query(
                func.date_trunc(trunc, CryptoOperation.created_at).label("bucket"),
                func.count(CryptoOperation.id),
            )
            .filter(CryptoOperation.created_at >= since)
            .group_by("bucket")
            .order_by("bucket")
            .all()
        )
        auth_rows = (
            self.db.query(
                func.date_trunc(trunc, SecurityLog.timestamp).label("bucket"),
                func.count(SecurityLog.id),
            )
            .filter(
                SecurityLog.timestamp >= since,
                SecurityLog.event_type == SecurityEventType.AUTH.value,
                SecurityLog.success.is_(False),
            )
            .group_by("bucket")
            .order_by("bucket")
            .all()
        )
        attack_rows = (
            self.db.query(
                func.date_trunc(trunc, AttackExperiment.created_at).label("bucket"),
                func.count(AttackExperiment.id),
            )
            .filter(AttackExperiment.created_at >= since)
            .group_by("bucket")
            .order_by("bucket")
            .all()
        )

        def _series(rows: list) -> list[dict]:
            return [
                {
                    "bucket": (b.isoformat() if hasattr(b, "isoformat") else str(b)),
                    "count": int(c),
                }
                for b, c in rows
                if b is not None
            ]

        return {
            "window_hours": hours,
            "bucket": bucket,
            "crypto_operations": _series(crypto_rows),
            "auth_failures": _series(auth_rows),
            "attack_experiments": _series(attack_rows),
        }

    def auth_failures(self, *, hours: int = 24, burst_threshold: int = 10) -> dict[str, Any]:
        self._ensure_enabled()
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        rows = (
            self.db.query(
                SecurityLog.ip_address,
                func.count(SecurityLog.id).label("failures"),
                func.min(SecurityLog.timestamp).label("first_seen"),
                func.max(SecurityLog.timestamp).label("last_seen"),
            )
            .filter(
                SecurityLog.timestamp >= since,
                SecurityLog.event_type == SecurityEventType.AUTH.value,
                SecurityLog.success.is_(False),
            )
            .group_by(SecurityLog.ip_address)
            .order_by(func.count(SecurityLog.id).desc())
            .limit(50)
            .all()
        )
        items = []
        bursts = 0
        for ip, failures, first_seen, last_seen in rows:
            is_burst = failures >= burst_threshold
            if is_burst:
                bursts += 1
            items.append(
                {
                    "ip_address": ip or "unknown",
                    "failures": int(failures),
                    "first_seen": first_seen.isoformat() if first_seen else None,
                    "last_seen": last_seen.isoformat() if last_seen else None,
                    "burst": is_burst,
                }
            )
        total = (
            self.db.query(func.count(SecurityLog.id))
            .filter(
                SecurityLog.timestamp >= since,
                SecurityLog.event_type == SecurityEventType.AUTH.value,
                SecurityLog.success.is_(False),
            )
            .scalar()
            or 0
        )
        return {
            "window_hours": hours,
            "burst_threshold": burst_threshold,
            "total_failures": int(total),
            "burst_ips": bursts,
            "by_ip": items,
        }

    def crypto_failures(self, *, hours: int = 24) -> dict[str, Any]:
        self._ensure_enabled()
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        total = (
            self.db.query(func.count(CryptoOperation.id))
            .filter(CryptoOperation.created_at >= since)
            .scalar()
            or 0
        )
        fails = (
            self.db.query(func.count(CryptoOperation.id))
            .filter(
                CryptoOperation.created_at >= since,
                CryptoOperation.success.is_(False),
            )
            .scalar()
            or 0
        )
        by_type = (
            self.db.query(
                CryptoOperation.operation_type,
                func.count(CryptoOperation.id),
                func.sum(case((CryptoOperation.success.is_(False), 1), else_=0)),
            )
            .filter(CryptoOperation.created_at >= since)
            .group_by(CryptoOperation.operation_type)
            .all()
        )
        return {
            "window_hours": hours,
            "total_operations": int(total),
            "failed_operations": int(fails),
            "failure_rate": round(fails / total, 6) if total else 0.0,
            "by_operation_type": [
                {
                    "operation_type": op,
                    "total": int(t),
                    "failures": int(f or 0),
                }
                for op, t, f in by_type
            ],
        }

    def seed_load(
        self,
        *,
        admin: User,
        crypto_events: int = 1000,
        auth_failures: int = 200,
        attack_events: int = 50,
        hours_span: int = 48,
    ) -> dict[str, int]:
        """Bulk-insert synthetic lab events for volume / dashboard demos."""
        self._ensure_enabled()
        if crypto_events < 0 or auth_failures < 0 or attack_events < 0:
            raise AppError("Counts must be non-negative", status_code=400)
        if crypto_events + auth_failures + attack_events > 50_000:
            raise AppError("Refusing to seed more than 50000 events at once", status_code=400)

        now = datetime.now(timezone.utc)
        span = timedelta(hours=max(hours_span, 1))
        op_types = [
            CryptoOperationType.ENCRYPT.value,
            CryptoOperationType.DECRYPT.value,
            CryptoOperationType.STEGO_EMBED.value,
            CryptoOperationType.METRIC_AVALANCHE.value,
            CryptoOperationType.ATTACK_DIFFERENTIAL.value,
        ]
        algorithms = [
            CryptoAlgorithm.CUSTOM_SPN.value,
            CryptoAlgorithm.AES_256_GCM.value,
        ]

        crypto_batch: list[CryptoOperation] = []
        for i in range(crypto_events):
            created = now - timedelta(
                seconds=random.randint(0, int(span.total_seconds()))
            )
            success = random.random() > 0.08
            crypto_batch.append(
                CryptoOperation(
                    id=uuid.uuid4(),
                    user_id=admin.id,
                    operation_type=random.choice(op_types),
                    algorithm=random.choice(algorithms),
                    input_kind=CryptoInputKind.TEXT.value,
                    input_size=random.randint(16, 2048),
                    output_size=random.randint(16, 4096),
                    success=success,
                    error_code=None if success else "SyntheticError",
                    avalanche_score=round(random.uniform(0.35, 0.55), 4) if success else None,
                    duration_ms=random.randint(1, 120),
                    details={"synthetic": True, "seed_batch": True},
                    created_at=created,
                )
            )
            if len(crypto_batch) >= 500:
                self.db.bulk_save_objects(crypto_batch)
                crypto_batch.clear()
        if crypto_batch:
            self.db.bulk_save_objects(crypto_batch)

        auth_batch: list[SecurityLog] = []
        ips = [f"203.0.113.{i}" for i in range(1, 16)] + ["198.51.100.10"]
        for _ in range(auth_failures):
            created = now - timedelta(
                seconds=random.randint(0, int(span.total_seconds()))
            )
            auth_batch.append(
                SecurityLog(
                    id=uuid.uuid4(),
                    user_id=None,
                    event_type=SecurityEventType.AUTH.value,
                    action="login_failed",
                    resource="auth",
                    ip_address=random.choice(ips),
                    user_agent="SecureRecruit-SeedBot/1.0",
                    success=False,
                    timestamp=created,
                    details="synthetic login failure for analytics volume",
                )
            )
            if len(auth_batch) >= 500:
                self.db.bulk_save_objects(auth_batch)
                auth_batch.clear()
        if auth_batch:
            self.db.bulk_save_objects(auth_batch)

        attack_types = [
            AttackType.BRUTE_FORCE.value,
            AttackType.DIFFERENTIAL.value,
            AttackType.STATISTICAL.value,
        ]
        attack_batch: list[AttackExperiment] = []
        for _ in range(attack_events):
            created = now - timedelta(
                seconds=random.randint(0, int(span.total_seconds()))
            )
            atype = random.choice(attack_types)
            score = round(random.uniform(0.05, 0.95), 4)
            attack_batch.append(
                AttackExperiment(
                    id=uuid.uuid4(),
                    user_id=admin.id,
                    attack_type=atype,
                    algorithm=CryptoAlgorithm.CUSTOM_SPN.value,
                    parameters={"synthetic": True},
                    result_summary="synthetic lab experiment",
                    metrics={"synthetic": True, "score": score},
                    effectiveness_score=score,
                    created_at=created,
                )
            )
        if attack_batch:
            self.db.bulk_save_objects(attack_batch)

        self.db.commit()
        return {
            "crypto_operations": crypto_events,
            "auth_failures": auth_failures,
            "attack_experiments": attack_events,
            "total": crypto_events + auth_failures + attack_events,
        }
