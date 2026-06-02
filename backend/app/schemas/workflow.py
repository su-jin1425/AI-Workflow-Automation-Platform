from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.execution.validator import validate_workflow_definition


class WorkflowCreate(BaseModel):
    workflow_name: str = Field(min_length=2, max_length=200)
    workflow_definition: dict[str, Any]
    status: Literal["draft", "active", "paused"] = "draft"

    @field_validator("workflow_definition")
    @classmethod
    def validate_definition(cls, value: dict[str, Any]) -> dict[str, Any]:
        validate_workflow_definition(value)
        return value


class WorkflowUpdate(BaseModel):
    workflow_name: str | None = Field(default=None, min_length=2, max_length=200)
    workflow_definition: dict[str, Any] | None = None
    status: Literal["draft", "active", "paused", "archived"] | None = None

    @field_validator("workflow_definition")
    @classmethod
    def validate_definition(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is not None:
            validate_workflow_definition(value)
        return value


class WorkflowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workflow_name: str
    workflow_definition: dict[str, Any]
    status: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
