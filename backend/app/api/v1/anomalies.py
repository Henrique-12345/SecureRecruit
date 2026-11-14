from uuid import UUID

from fastapi import APIRouter, Query, Request

from app.dependencies.auth import AdminUser, DbSession
from app.schemas.anomaly import (
    AnomalyEventRead,
    AnomalyResolveResponse,
    AnomalyRunRequest,
    AnomalyRunResponse,
)
from app.services.anomaly.anomaly_service import AnomalyService
from app.utils.request import get_client_ip, get_user_agent


router = APIRouter(prefix="/anomalies", tags=["anomalies"])


@router.post("/run", response_model=AnomalyRunResponse)
def run_detection(
    payload: AnomalyRunRequest,
    request: Request,
    admin: AdminUser,
    db: DbSession,
) -> AnomalyRunResponse:
    created = AnomalyService(db).run_detection(
        admin=admin,
        hours=payload.hours,
        auth_burst_threshold=payload.auth_burst_threshold,
        decrypt_fail_rate_threshold=payload.decrypt_fail_rate_threshold,
        access_denied_threshold=payload.access_denied_threshold,
        event_spike_z=payload.event_spike_z,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return AnomalyRunResponse(
        created_count=len(created),
        anomalies=[AnomalyEventRead.model_validate(a) for a in created],
    )


@router.get("", response_model=list[AnomalyEventRead])
def list_anomalies(
    _: AdminUser,
    db: DbSession,
    resolved: bool | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[AnomalyEventRead]:
    items = AnomalyService(db).list_anomalies(resolved=resolved, limit=limit)
    return [AnomalyEventRead.model_validate(a) for a in items]


@router.get("/{anomaly_id}", response_model=AnomalyEventRead)
def get_anomaly(anomaly_id: UUID, _: AdminUser, db: DbSession) -> AnomalyEventRead:
    event = AnomalyService(db).get_anomaly(anomaly_id)
    return AnomalyEventRead.model_validate(event)


@router.patch("/{anomaly_id}/resolve", response_model=AnomalyResolveResponse)
def resolve_anomaly(
    anomaly_id: UUID,
    request: Request,
    admin: AdminUser,
    db: DbSession,
) -> AnomalyResolveResponse:
    event = AnomalyService(db).resolve(
        anomaly_id=anomaly_id,
        admin=admin,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    return AnomalyResolveResponse(anomaly=AnomalyEventRead.model_validate(event))
