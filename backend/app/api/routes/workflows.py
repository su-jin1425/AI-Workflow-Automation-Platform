from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.workflow import (
    WorkflowCreate,
    WorkflowResponse,
    WorkflowUpdate,
)
from app.schemas.workflow_version import (
    WorkflowVersionResponse,
)
from app.services.workflow_service import WorkflowService
from app.services.workflow_version_service import (
    WorkflowVersionService,
)

router = APIRouter(
    prefix="/workflows",
    tags=["workflows"],
)


@router.post(
    "",
    response_model=WorkflowResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_workflow(
    payload: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await WorkflowService(
        db
    ).create(
        payload,
        user,
    )


@router.get(
    "",
    response_model=list[WorkflowResponse],
)
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await WorkflowService(
        db
    ).list_for_user(
        user
    )


@router.get(
    "/{workflow_id}",
    response_model=WorkflowResponse,
)
async def get_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    workflow = await WorkflowService(
        db
    ).get_owned(
        workflow_id,
        user,
    )

    if workflow is None:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found",
        )

    return workflow


@router.put(
    "/{workflow_id}",
    response_model=WorkflowResponse,
)
async def update_workflow(
    workflow_id: UUID,
    payload: WorkflowUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    workflow = await WorkflowService(
        db
    ).update(
        workflow_id,
        payload,
        user,
    )

    if workflow is None:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found",
        )

    return workflow


@router.delete(
    "/{workflow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_workflow(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    deleted = await WorkflowService(
        db
    ).delete(
        workflow_id,
        user,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found",
        )


@router.get(
    "/{workflow_id}/versions",
    response_model=list[
        WorkflowVersionResponse
    ],
)
async def list_versions(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await WorkflowVersionService(
        db
    ).list_versions(
        workflow_id,
        user,
    )


@router.get(
    "/{workflow_id}/versions/{version_number}",
    response_model=WorkflowVersionResponse,
)
async def get_version(
    workflow_id: UUID,
    version_number: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    version = await WorkflowVersionService(
        db
    ).get_version(
        workflow_id,
        version_number,
        user,
    )

    if version is None:
        raise HTTPException(
            status_code=404,
            detail="Version not found",
        )

    return version


@router.post(
    "/{workflow_id}/rollback/{version_number}",
    response_model=WorkflowResponse,
)
async def rollback_workflow(
    workflow_id: UUID,
    version_number: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    workflow = await WorkflowVersionService(
        db
    ).rollback(
        workflow_id,
        version_number,
        user,
    )

    if workflow is None:
        raise HTTPException(
            status_code=404,
            detail="Version not found",
        )

    return workflow