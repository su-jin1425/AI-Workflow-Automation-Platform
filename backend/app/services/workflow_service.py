from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.workflow import Workflow, WorkflowNode
from app.models.workflow_version import WorkflowVersion
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate


class WorkflowService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        payload: WorkflowCreate,
        user: User,
    ) -> Workflow:

        workflow = Workflow(
            workflow_name=payload.workflow_name,
            workflow_definition=payload.workflow_definition,
            status=payload.status,
            created_by=user.id,
            current_version=1,
        )

        self.db.add(workflow)

        await self.db.flush()

        self.db.add(
            WorkflowVersion(
                workflow_id=workflow.id,
                version_number=1,
                workflow_definition=payload.workflow_definition,
                change_note="Initial version",
                is_published=True,
            )
        )

        self._sync_nodes(
            workflow,
            payload.workflow_definition,
        )

        await self.db.commit()

        await self.db.refresh(workflow)

        return workflow

    async def list_for_user(
        self,
        user: User,
    ) -> list[Workflow]:

        result = await self.db.execute(
            select(Workflow)
            .where(
                Workflow.created_by == user.id
            )
            .order_by(
                Workflow.created_at.desc()
            )
        )

        return list(
            result.scalars().all()
        )

    async def get_owned(
        self,
        workflow_id: UUID,
        user: User,
    ) -> Workflow | None:

        result = await self.db.execute(
            select(Workflow).where(
                Workflow.id == workflow_id,
                Workflow.created_by == user.id,
            )
        )

        return result.scalar_one_or_none()

    async def update(
        self,
        workflow_id: UUID,
        payload: WorkflowUpdate,
        user: User,
    ) -> Workflow | None:

        workflow = await self.get_owned(
            workflow_id,
            user,
        )

        if workflow is None:
            return None

        if payload.workflow_name is not None:
            workflow.workflow_name = (
                payload.workflow_name
            )

        if payload.workflow_definition is not None:

            workflow.current_version += 1

            workflow.workflow_definition = (
                payload.workflow_definition
            )

            await self.db.execute(
                delete(WorkflowNode).where(
                    WorkflowNode.workflow_id
                    == workflow.id
                )
            )

            self._sync_nodes(
                workflow,
                payload.workflow_definition,
            )

            self.db.add(
                WorkflowVersion(
                    workflow_id=workflow.id,
                    version_number=workflow.current_version,
                    workflow_definition=payload.workflow_definition,
                    change_note=f"Version {workflow.current_version}",
                    is_published=True,
                )
            )

        if payload.status is not None:
            workflow.status = payload.status

        await self.db.commit()

        await self.db.refresh(workflow)

        return workflow

    async def delete(
        self,
        workflow_id: UUID,
        user: User,
    ) -> bool:

        workflow = await self.get_owned(
            workflow_id,
            user,
        )

        if workflow is None:
            return False

        await self.db.delete(workflow)

        await self.db.commit()

        return True

    def _sync_nodes(
        self,
        workflow: Workflow,
        definition: dict,
    ) -> None:

        for node in definition.get(
            "nodes",
            [],
        ):

            position = node.get(
                "position",
                {},
            )

            self.db.add(
                WorkflowNode(
                    workflow_id=workflow.id,
                    node_key=node["id"],
                    node_type=node["type"],
                    configuration=node.get(
                        "configuration",
                        {},
                    ),
                    position_x=int(
                        position.get(
                            "x",
                            0,
                        )
                    ),
                    position_y=int(
                        position.get(
                            "y",
                            0,
                        )
                    ),
                )
            )