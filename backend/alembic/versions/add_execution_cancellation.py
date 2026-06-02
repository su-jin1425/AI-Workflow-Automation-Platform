from alembic import op
import sqlalchemy as sa

revision = "add_execution_cancellation"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "workflow_executions",
        sa.Column(
            "cancel_requested",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )

    op.add_column(
        "workflow_executions",
        sa.Column(
            "cancelled_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column(
        "workflow_executions",
        "cancelled_at",
    )

    op.drop_column(
        "workflow_executions",
        "cancel_requested",
    )