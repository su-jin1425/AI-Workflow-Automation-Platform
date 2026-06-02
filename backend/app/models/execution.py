from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class WorkflowExecution(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workflow_executions"

    workflow_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workflows.id"),
        nullable=False,
    )

    execution_status: Mapped[str] = mapped_column(
        String(30),
        default="queued",
        nullable=False,
    )

    input_payload: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    output_payload: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    cancel_requested: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    execution_logs: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    workflow = relationship(
        "Workflow",
        back_populates="executions",
    )

    node_executions = relationship(
        "NodeExecution",
        back_populates="execution",
        cascade="all,delete",
    )

    metrics = relationship(
        "ExecutionMetric",
        back_populates="execution",
        cascade="all,delete",
    )


class NodeExecution(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "node_executions"

    execution_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workflow_executions.id"),
        nullable=False,
    )

    node_id: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    node_type: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="queued",
        nullable=False,
    )

    input_payload: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    output_payload: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    execution = relationship(
        "WorkflowExecution",
        back_populates="node_executions",
    )


class ExecutionMetric(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "execution_metrics"

    execution_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workflow_executions.id"),
        nullable=False,
    )

    execution_time: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
    )

    token_usage: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    api_calls: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    execution = relationship(
        "WorkflowExecution",
        back_populates="metrics",
    )