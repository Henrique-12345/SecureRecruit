from fastapi import APIRouter, Query

from app.dependencies.auth import AdminUser, DbSession
from app.models.security_log import SecurityLog
from app.schemas.security_log import SecurityLogRead


router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("", response_model=list[SecurityLogRead])
def list_logs(
    _: AdminUser,
    db: DbSession,
    limit: int = Query(default=100, ge=1, le=500),
) -> list[SecurityLogRead]:
    logs = (
        db.query(SecurityLog)
        .order_by(SecurityLog.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [SecurityLogRead.model_validate(log) for log in logs]
