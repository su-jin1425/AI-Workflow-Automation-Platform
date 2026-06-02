from uuid import UUID

from app.db.session import async_session_maker
from app.execution.engine import WorkflowEngine


async def run_workflow_execution(execution_id: str) -> None:
    async with async_session_maker() as db:
        await WorkflowEngine(db).run(UUID(execution_id))
