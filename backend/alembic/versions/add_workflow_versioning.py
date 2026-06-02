from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "add_workflow_versioning"
down_revision = "add_execution_cancellation"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.add_column(
        "workflows",
        sa.Column(
            "current_version",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )

    op.create_table(
        "workflow_versions",

        sa.Column(
            "workflow_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),

        sa.Column(
            "version_number",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "workflow_definition",
            sa.JSON(),
            nullable=False,
        ),

        sa.Column(
            "change_note",
            sa.String(length=500),
            nullable=False,
            server_default="",
        ),

        sa.Column(
            "is_published",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),

        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
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

        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["workflows.id"],
        ),

        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:

    op.drop_table(
        "workflow_versions"
    )

    op.drop_column(
        "workflows",
        "current_version"
    )