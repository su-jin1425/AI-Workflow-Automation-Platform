from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.workflow import Workflow
from app.models.workflow_version import WorkflowVersion


class WorkflowVersionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_versions(
        self,
        workflow_id: UUID,
        user: User,
    ) -> list[WorkflowVersion]:
        workflow = await self._get_workflow(
            workflow_id,
            user,
        )

        if workflow is None:
            return []

        result = await self.db.execute(
            select(WorkflowVersion)
            .where(
                WorkflowVersion.workflow_id
                == workflow_id
            )
            .order_by(
                WorkflowVersion.version_number.desc()
            )
        )

        return list(
            result.scalars().all()
        )

    async def get_version(
        self,
        workflow_id: UUID,
        version_number: int,
        user: User,
    ) -> WorkflowVersion | None:
        workflow = await self._get_workflow(
            workflow_id,
            user,
        )

        if workflow is None:
            return None

        result = await self.db.execute(
            select(WorkflowVersion)
            .where(
                WorkflowVersion.workflow_id
                == workflow_id,
                WorkflowVersion.version_number
                == version_number,
            )
        )

        return result.scalar_one_or_none()

    async def rollback(
        self,
        workflow_id: UUID,
        version_number: int,
        user: User,
    ) -> Workflow | None:
        workflow = await self._get_workflow(
            workflow_id,
            user,
        )

        if workflow is None:
            return None

        version = await self.get_version(
            workflow_id,
            version_number,
            user,
        )

        if version is None:
            return None

        workflow.workflow_definition = (
            version.workflow_definition
        )

        workflow.current_version += 1

        rollback_version = WorkflowVersion(
            workflow_id=workflow.id,
            version_number=workflow.current_version,
            workflow_definition=version.workflow_definition,
            change_note=(
                f"Rollback to version "
                f"{version_number}"
            ),
            is_published=True,
        )

        self.db.add(
            rollback_version
        )

        await self.db.commit()

        await self.db.refresh(
            workflow
        )

        return workflow

    async def _get_workflow(
        self,
        workflow_id: UUID,
        user: User,
    ) -> Workflow | None:
        result = await self.db.execute(
            select(Workflow)
            .where(
                Workflow.id == workflow_id,
                Workflow.created_by == user.id,
            )
        )

        return result.scalar_one_or_none()