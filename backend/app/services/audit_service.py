from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.user import User


class AuditService:
    def __init__(
        self,
        db: AsyncSession,
    ):
        self.db = db

    async def log(
        self,
        *,
        user: User,
        action: str,
        resource_type: str,
        resource_id: UUID | str,
        details: str | None = None,
    ) -> None:
        audit = AuditLog(
            user_id=user.id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            details=details,
        )

        self.db.add(audit)