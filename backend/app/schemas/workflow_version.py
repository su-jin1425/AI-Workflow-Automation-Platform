from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WorkflowVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workflow_id: UUID
    version_number: int
    workflow_definition: dict
    change_note: str | None
    is_published: bool
    created_at: datetime