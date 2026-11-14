from fastapi import APIRouter, Query, Request

from app.dependencies.auth import AdminUser, DbSession
from app.schemas.analytics import SeedLoadRequest, SeedLoadResponse
from app.services.analytics_service import AnalyticsService
from app.utils.request import get_client_ip, get_user_agent
from app.core.enums import SecurityEventType
from app.services.audit_service import AuditService


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/events/summary")
def events_summary(
    _: AdminUser,
    db: DbSession,
    hours: int = Query(default=24, ge=1, le=720),
) -> dict:
    return AnalyticsService(db).events_summary(hours=hours)


@router.get("/events/timeseries")
def events_timeseries(
    _: AdminUser,
    db: DbSession,
    hours: int = Query(default=24, ge=1, le=720),
    bucket: str = Query(default="hour", pattern="^(hour|day)$"),
) -> dict:
    return AnalyticsService(db).events_timeseries(hours=hours, bucket=bucket)


@router.get("/auth/failures")
def auth_failures(
    _: AdminUser,
    db: DbSession,
    hours: int = Query(default=24, ge=1, le=720),
    burst_threshold: int = Query(default=10, ge=1, le=1000),
) -> dict:
    return AnalyticsService(db).auth_failures(hours=hours, burst_threshold=burst_threshold)


@router.get("/crypto/failures")
def crypto_failures(
    _: AdminUser,
    db: DbSession,
    hours: int = Query(default=24, ge=1, le=720),
) -> dict:
    return AnalyticsService(db).crypto_failures(hours=hours)


@router.post("/seed-load", response_model=SeedLoadResponse)
def seed_load(
    payload: SeedLoadRequest,
    request: Request,
    admin: AdminUser,
    db: DbSession,
) -> SeedLoadResponse:
    result = AnalyticsService(db).seed_load(
        admin=admin,
        crypto_events=payload.crypto_events,
        auth_failures=payload.auth_failures,
        attack_events=payload.attack_events,
        hours_span=payload.hours_span,
    )
    AuditService(db).log_event(
        event_type=SecurityEventType.ADMIN,
        action="analytics_seed_load",
        success=True,
        user_id=admin.id,
        resource="analytics",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        details=f"seeded total={result['total']}",
    )
    return SeedLoadResponse(**result)
