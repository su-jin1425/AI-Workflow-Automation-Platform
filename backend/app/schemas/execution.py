from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExecutionStartRequest(BaseModel):
    workflow_id: UUID
    input_payload: dict[str, Any] = Field(default_factory=dict)


class ExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workflow_id: UUID

    execution_status: str

    cancel_requested: bool = False

    input_payload: dict[str, Any]

    output_payload: dict[str, Any] | None

    started_at: datetime | None

    completed_at: datetime | None

    cancelled_at: datetime | None

    execution_logs: list[Any]

    created_at: datetime