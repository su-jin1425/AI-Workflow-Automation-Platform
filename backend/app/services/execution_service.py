from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.execution import WorkflowExecution
from app.models.user import User
from app.models.workflow import Workflow


class ExecutionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_execution(
        self,
        workflow_id: UUID,
        input_payload: dict,
        user: User,
    ) -> WorkflowExecution | None:
        workflow_result = await self.db.execute(
            select(Workflow).where(
                Workflow.id == workflow_id,
                Workflow.created_by == user.id,
            )
        )

        workflow = workflow_result.scalar_one_or_none()

        if workflow is None:
            return None

        execution = WorkflowExecution(
            workflow_id=workflow.id,
            input_payload=input_payload,
            execution_status="queued",
            execution_logs=[],
            cancel_requested=False,
        )

        self.db.add(execution)

        await self.db.commit()
        await self.db.refresh(execution)

        return execution

    async def cancel_execution(
        self,
        execution_id: UUID,
        user: User,
    ) -> WorkflowExecution | None:
        execution = await self.get_owned(
            execution_id,
            user,
        )

        if execution is None:
            return None

        if execution.execution_status in {
            "completed",
            "failed",
            "cancelled",
        }:
            return execution

        execution.cancel_requested = True

        await self.db.commit()
        await self.db.refresh(execution)

        return execution

    async def list_for_user(
        self,
        user: User,
    ) -> list[WorkflowExecution]:
        result = await self.db.execute(
            select(WorkflowExecution)
            .join(Workflow)
            .where(
                Workflow.created_by == user.id
            )
            .order_by(
                WorkflowExecution.created_at.desc()
            )
        )

        return list(
            result.scalars().all()
        )

    async def get_owned(
        self,
        execution_id: UUID,
        user: User,
    ) -> WorkflowExecution | None:
        result = await self.db.execute(
            select(WorkflowExecution)
            .join(Workflow)
            .where(
                WorkflowExecution.id == execution_id,
                Workflow.created_by == user.id,
            )
        )

        return result.scalar_one_or_none()

    async def get_logs(
        self,
        execution_id: UUID,
        user: User,
    ) -> list | None:
        execution = await self.get_owned(
            execution_id,
            user,
        )

        if execution is None:
            return None

        return execution.execution_logs