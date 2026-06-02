from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
async def overview(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await AnalyticsService(db).overview(user)


@router.get("/executions")
async def executions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await AnalyticsService(db).execution_summary(user)


@router.get("/system-health")
async def system_health():
    return await AnalyticsService.system_health()
