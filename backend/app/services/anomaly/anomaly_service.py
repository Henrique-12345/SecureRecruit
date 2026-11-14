"""Rule-based + lightweight statistical anomaly detection (Unit 2 Phase 6)."""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.enums import (
    AnomalySeverity,
    AnomalyType,
    CryptoOperationType,
    SecurityEventType,
)
from app.core.exceptions import NotFoundError
from app.models.anomaly_event import AnomalyEvent
from app.models.crypto_operation import CryptoOperation
from app.models.resume import Resume
from app.models.security_log import SecurityLog
from app.models.user import User
from app.services.audit_service import AuditService
from app.services.crypto.guards import ensure_crypto_lab_enabled
from app.services.hash_service import verify_file_integrity


@dataclass
class DetectionHit:
    anomaly_type: str
    severity: str
    score: float
    source_user_id: UUID | None
    evidence: dict[str, Any]


class AnomalyService:
    def __init__(self, db: Session):
        self.db = db

    def _ensure_enabled(self) -> None:
        ensure_crypto_lab_enabled()

    def run_detection(
        self,
        *,
        admin: User,
        hours: int = 24,
        auth_burst_threshold: int = 20,
        decrypt_fail_rate_threshold: float = 0.25,
        access_denied_threshold: int = 30,
        event_spike_z: float = 2.5,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> list[AnomalyEvent]:
        self._ensure_enabled()
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        hits: list[DetectionHit] = []
        hits.extend(self._detect_auth_burst(since, auth_burst_threshold))
        hits.extend(
            self._detect_decrypt_fail_rate(since, decrypt_fail_rate_threshold)
        )
        hits.extend(self._detect_file_integrity())
        hits.extend(self._detect_access_pattern(since, access_denied_threshold))
        hits.extend(self._detect_event_spike(hours=hours, z_threshold=event_spike_z))

        created: list[AnomalyEvent] = []
        for hit in hits:
            if self._recent_unresolved_exists(hit.anomaly_type, hours=hours):
                continue
            event = AnomalyEvent(
                anomaly_type=hit.anomaly_type,
                severity=hit.severity,
                score=hit.score,
                source_user_id=hit.source_user_id,
                evidence=hit.evidence,
                resolved=False,
            )
            self.db.add(event)
            created.append(event)

        self.db.commit()
        for event in created:
            self.db.refresh(event)
            AuditService(self.db).log_event(
                event_type=SecurityEventType.ANOMALY,
                action="anomaly_detected",
                success=True,
                user_id=admin.id,
                resource="anomaly_event",
                resource_id=event.id,
                ip_address=ip_address,
                user_agent=user_agent,
                details=(
                    f"type={event.anomaly_type} severity={event.severity} "
                    f"score={event.score:.1f}"
                ),
            )
        return created

    def list_anomalies(
        self, *, resolved: bool | None = None, limit: int = 50
    ) -> list[AnomalyEvent]:
        self._ensure_enabled()
        q = self.db.query(AnomalyEvent).order_by(AnomalyEvent.detected_at.desc())
        if resolved is not None:
            q = q.filter(AnomalyEvent.resolved.is_(resolved))
        return q.limit(min(limit, 200)).all()

    def get_anomaly(self, anomaly_id: UUID) -> AnomalyEvent:
        self._ensure_enabled()
        event = self.db.query(AnomalyEvent).filter(AnomalyEvent.id == anomaly_id).first()
        if not event:
            raise NotFoundError("Anomaly event not found")
        return event

    def resolve(
        self,
        *,
        anomaly_id: UUID,
        admin: User,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AnomalyEvent:
        self._ensure_enabled()
        event = self.get_anomaly(anomaly_id)
        event.resolved = True
        self.db.commit()
        self.db.refresh(event)
        AuditService(self.db).log_event(
            event_type=SecurityEventType.ANOMALY,
            action="anomaly_resolved",
            success=True,
            user_id=admin.id,
            resource="anomaly_event",
            resource_id=event.id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=f"resolved type={event.anomaly_type}",
        )
        return event

    def _recent_unresolved_exists(self, anomaly_type: str, *, hours: int) -> bool:
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        existing = (
            self.db.query(AnomalyEvent.id)
            .filter(
                AnomalyEvent.anomaly_type == anomaly_type,
                AnomalyEvent.resolved.is_(False),
                AnomalyEvent.detected_at >= since,
            )
            .first()
        )
        return existing is not None

    def _detect_auth_burst(self, since: datetime, threshold: int) -> list[DetectionHit]:
        rows = (
            self.db.query(
                SecurityLog.ip_address,
                func.count(SecurityLog.id),
            )
            .filter(
                SecurityLog.timestamp >= since,
                SecurityLog.event_type == SecurityEventType.AUTH.value,
                SecurityLog.success.is_(False),
            )
            .group_by(SecurityLog.ip_address)
            .all()
        )
        hits: list[DetectionHit] = []
        total = sum(int(c) for _, c in rows)
        # Global burst OR per-IP burst
        burst_ips = [
            {"ip": ip or "unknown", "failures": int(c)}
            for ip, c in rows
            if int(c) >= max(5, threshold // 4)
        ]
        if total >= threshold or burst_ips:
            score = min(100.0, 40.0 + total * 1.2)
            severity = (
                AnomalySeverity.HIGH.value
                if total >= threshold * 2
                else AnomalySeverity.MEDIUM.value
            )
            if total >= threshold or any(b["failures"] >= threshold for b in burst_ips):
                hits.append(
                    DetectionHit(
                        anomaly_type=AnomalyType.AUTH_BURST.value,
                        severity=severity,
                        score=round(score, 2),
                        source_user_id=None,
                        evidence={
                            "window_since": since.isoformat(),
                            "total_failures": total,
                            "threshold": threshold,
                            "by_ip": sorted(
                                [
                                    {"ip": ip or "unknown", "failures": int(c)}
                                    for ip, c in rows
                                ],
                                key=lambda x: x["failures"],
                                reverse=True,
                            )[:20],
                            "detector": "rule_auth_burst",
                        },
                    )
                )
        return hits

    def _detect_decrypt_fail_rate(
        self, since: datetime, threshold: float
    ) -> list[DetectionHit]:
        total = (
            self.db.query(func.count(CryptoOperation.id))
            .filter(
                CryptoOperation.created_at >= since,
                CryptoOperation.operation_type == CryptoOperationType.DECRYPT.value,
            )
            .scalar()
            or 0
        )
        if total < 5:
            return []
        fails = (
            self.db.query(func.count(CryptoOperation.id))
            .filter(
                CryptoOperation.created_at >= since,
                CryptoOperation.operation_type == CryptoOperationType.DECRYPT.value,
                CryptoOperation.success.is_(False),
            )
            .scalar()
            or 0
        )
        rate = fails / total
        if rate < threshold:
            return []
        score = min(100.0, 50.0 + rate * 100.0)
        severity = (
            AnomalySeverity.HIGH.value if rate >= 0.5 else AnomalySeverity.MEDIUM.value
        )
        return [
            DetectionHit(
                anomaly_type=AnomalyType.DECRYPT_FAIL_RATE.value,
                severity=severity,
                score=round(score, 2),
                source_user_id=None,
                evidence={
                    "window_since": since.isoformat(),
                    "decrypt_total": int(total),
                    "decrypt_failures": int(fails),
                    "failure_rate": round(rate, 6),
                    "threshold": threshold,
                    "detector": "rule_decrypt_fail_rate",
                },
            )
        ]

    def _detect_file_integrity(self) -> list[DetectionHit]:
        mismatches: list[dict[str, Any]] = []
        resumes = self.db.query(Resume).limit(200).all()
        for resume in resumes:
            path = Path(resume.file_path)
            if not path.exists():
                mismatches.append(
                    {
                        "resume_id": str(resume.id),
                        "reason": "missing_file",
                        "expected_hash": resume.sha256_hash,
                    }
                )
                continue
            current, ok = verify_file_integrity(path, resume.sha256_hash)
            if not ok:
                mismatches.append(
                    {
                        "resume_id": str(resume.id),
                        "reason": "hash_mismatch",
                        "expected_hash": resume.sha256_hash,
                        "current_hash": current,
                    }
                )
        if not mismatches:
            return []
        score = min(100.0, 60.0 + 10.0 * len(mismatches))
        return [
            DetectionHit(
                anomaly_type=AnomalyType.FILE_INTEGRITY.value,
                severity=AnomalySeverity.HIGH.value,
                score=round(score, 2),
                source_user_id=None,
                evidence={
                    "mismatch_count": len(mismatches),
                    "samples": mismatches[:20],
                    "detector": "rule_file_integrity",
                },
            )
        ]

    def _detect_access_pattern(
        self, since: datetime, threshold: int
    ) -> list[DetectionHit]:
        total = (
            self.db.query(func.count(SecurityLog.id))
            .filter(
                SecurityLog.timestamp >= since,
                SecurityLog.event_type == SecurityEventType.ACCESS.value,
                SecurityLog.action == "access_denied",
                SecurityLog.success.is_(False),
            )
            .scalar()
            or 0
        )
        if total < threshold:
            return []
        by_user = (
            self.db.query(SecurityLog.user_id, func.count(SecurityLog.id))
            .filter(
                SecurityLog.timestamp >= since,
                SecurityLog.event_type == SecurityEventType.ACCESS.value,
                SecurityLog.action == "access_denied",
            )
            .group_by(SecurityLog.user_id)
            .order_by(func.count(SecurityLog.id).desc())
            .limit(10)
            .all()
        )
        top_user = by_user[0][0] if by_user else None
        score = min(100.0, 35.0 + total * 1.0)
        return [
            DetectionHit(
                anomaly_type=AnomalyType.ACCESS_PATTERN.value,
                severity=(
                    AnomalySeverity.HIGH.value
                    if total >= threshold * 2
                    else AnomalySeverity.MEDIUM.value
                ),
                score=round(score, 2),
                source_user_id=top_user,
                evidence={
                    "window_since": since.isoformat(),
                    "access_denied_count": int(total),
                    "threshold": threshold,
                    "top_users": [
                        {"user_id": str(uid) if uid else None, "count": int(c)}
                        for uid, c in by_user
                    ],
                    "detector": "rule_access_pattern",
                },
            )
        ]

    def _detect_event_spike(self, *, hours: int, z_threshold: float) -> list[DetectionHit]:
        # Compare last hour volume vs previous hourly buckets in the window
        now = datetime.now(timezone.utc)
        buckets: list[int] = []
        for i in range(hours, 0, -1):
            start = now - timedelta(hours=i)
            end = now - timedelta(hours=i - 1)
            count = (
                self.db.query(func.count(CryptoOperation.id))
                .filter(
                    CryptoOperation.created_at >= start,
                    CryptoOperation.created_at < end,
                )
                .scalar()
                or 0
            )
            buckets.append(int(count))
        if len(buckets) < 3:
            return []
        current = buckets[-1]
        baseline = buckets[:-1]
        mean = statistics.mean(baseline)
        stdev = statistics.pstdev(baseline) if len(baseline) > 1 else 0.0
        if stdev < 1e-6:
            if current > mean * 3 and current >= 50:
                z = 3.0
            else:
                return []
        else:
            z = (current - mean) / stdev
        if z < z_threshold:
            return []
        score = min(100.0, 40.0 + z * 15.0)
        return [
            DetectionHit(
                anomaly_type=AnomalyType.EVENT_SPIKE.value,
                severity=(
                    AnomalySeverity.HIGH.value if z >= 4 else AnomalySeverity.MEDIUM.value
                ),
                score=round(score, 2),
                source_user_id=None,
                evidence={
                    "current_hour_count": current,
                    "baseline_mean": round(mean, 2),
                    "baseline_stdev": round(stdev, 2),
                    "z_score": round(z, 4),
                    "z_threshold": z_threshold,
                    "detector": "zscore_event_spike",
                    "method_note": "Statistical z-score over hourly CryptoOperation counts",
                },
            )
        ]
