from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.execution import ExecutionMetric, WorkflowExecution
from app.models.user import User
from app.models.workflow import Workflow
from app.services.monitoring_service import MonitoringService


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def overview(self, user: User) -> dict:
        result = await self.db.execute(
            select(
                func.count(Workflow.id),
                func.count(WorkflowExecution.id),
                func.sum(case((WorkflowExecution.execution_status == "completed", 1), else_=0)),
                func.sum(case((WorkflowExecution.execution_status == "failed", 1), else_=0)),
            )
            .select_from(Workflow)
            .outerjoin(WorkflowExecution)
            .where(Workflow.created_by == user.id)
        )
        workflows, executions, completed, failed = result.one()
        return {
            "workflows": workflows or 0,
            "executions": executions or 0,
            "completed": completed or 0,
            "failed": failed or 0,
        }

    async def execution_summary(self, user: User) -> dict:
        result = await self.db.execute(
            select(
                func.avg(ExecutionMetric.execution_time),
                func.sum(ExecutionMetric.token_usage),
                func.sum(ExecutionMetric.api_calls),
            )
            .select_from(ExecutionMetric)
            .join(WorkflowExecution)
            .join(Workflow)
            .where(Workflow.created_by == user.id)
        )
        avg_time, token_usage, api_calls = result.one()
        return {
            "average_execution_time": float(avg_time or 0),
            "token_usage": int(token_usage or 0),
            "api_calls": int(api_calls or 0),
        }

    @staticmethod
    async def system_health() -> dict:
        queue = await MonitoringService.queue_status()
        return {"status": "healthy", "queue": queue}
