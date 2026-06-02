from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.execution.runner import run_workflow_execution
from app.models.user import User
from app.schemas.execution import ExecutionResponse, ExecutionStartRequest
from app.services.execution_service import ExecutionService
from app.tasks import execute_workflow_task

router = APIRouter(
    prefix="/executions",
    tags=["executions"],
)


@router.post(
    "/start",
    response_model=ExecutionResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_execution(
    payload: ExecutionStartRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service = ExecutionService(db)

    execution = await service.create_execution(
        payload.workflow_id,
        payload.input_payload,
        user,
    )

    if execution is None:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found",
        )

    if settings.execution_mode == "celery":
        execute_workflow_task.delay(
            str(execution.id)
        )
    else:
        background_tasks.add_task(
            run_workflow_execution,
            str(execution.id),
        )

    return execution


@router.post(
    "/{execution_id}/cancel",
    response_model=ExecutionResponse,
)
async def cancel_execution(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    execution = await ExecutionService(
        db
    ).cancel_execution(
        execution_id,
        user,
    )

    if execution is None:
        raise HTTPException(
            status_code=404,
            detail="Execution not found",
        )

    return execution


@router.get(
    "",
    response_model=list[ExecutionResponse],
)
async def list_executions(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await ExecutionService(
        db
    ).list_for_user(user)


@router.get(
    "/{execution_id}",
    response_model=ExecutionResponse,
)
async def get_execution(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    execution = await ExecutionService(
        db
    ).get_owned(
        execution_id,
        user,
    )

    if execution is None:
        raise HTTPException(
            status_code=404,
            detail="Execution not found",
        )

    return execution


@router.get("/logs/{execution_id}")
async def get_execution_logs(
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    logs = await ExecutionService(
        db
    ).get_logs(
        execution_id,
        user,
    )

    if logs is None:
        raise HTTPException(
            status_code=404,
            detail="Execution not found",
        )

    return {
        "execution_id": execution_id,
        "logs": logs,
    }