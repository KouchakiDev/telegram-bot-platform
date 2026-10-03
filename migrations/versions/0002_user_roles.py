"""Add reusable platform user roles."""
from alembic import op
import sqlalchemy as sa

revision = "0002_user_roles"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("role", sa.String(64), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("telegram_id", "role", name="uq_user_roles"),
    )
    op.create_index("ix_user_roles_telegram_id", "user_roles", ["telegram_id"])
    op.create_index("ix_user_roles_is_active", "user_roles", ["is_active"])


def downgrade() -> None:
    op.drop_table("user_roles")
