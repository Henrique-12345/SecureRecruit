from uuid import UUID

from sqlalchemy.orm import Session

from app.core.enums import SecurityEventType
from app.models.security_log import SecurityLog
from app.utils.masking import mask_email


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def log_event(
        self,
        *,
        event_type: str | SecurityEventType,
        action: str,
        success: bool = True,
        user_id: UUID | None = None,
        resource: str | None = None,
        resource_id: str | UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        details: str | None = None,
    ) -> SecurityLog:
        # Never persist secrets; mask emails that may appear in details.
        safe_details = details
        if safe_details and "@" in safe_details:
            # best-effort masking of emails inside free-text details
            tokens = safe_details.split()
            safe_details = " ".join(
                mask_email(t) if "@" in t and "." in t else t for t in tokens
            )

        entry = SecurityLog(
            user_id=user_id,
            event_type=event_type.value if isinstance(event_type, SecurityEventType) else event_type,
            action=action,
            resource=resource,
            resource_id=str(resource_id) if resource_id is not None else None,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            details=safe_details,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry
