from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class WorkflowVersion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workflow_versions"

    workflow_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("workflows.id"),
        nullable=False,
    )

    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    workflow_definition: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    change_note: Mapped[str] = mapped_column(
        String(500),
        default="",
        nullable=False,
    )

    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    workflow = relationship(
        "Workflow",
        back_populates="versions",
    )