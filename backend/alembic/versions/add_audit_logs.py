from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "add_audit_logs"
down_revision = "add_workflow_versioning"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "audit_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "action",
            sa.String(100),
            nullable=False,
        ),
        sa.Column(
            "resource_type",
            sa.String(100),
            nullable=False,
        ),
        sa.Column(
            "resource_id",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "details",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
    )


def downgrade():
    op.drop_table("audit_logs")