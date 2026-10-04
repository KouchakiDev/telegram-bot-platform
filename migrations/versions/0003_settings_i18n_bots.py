"""Add centralized settings, localization and bot profile catalogs.

Revision ID: 0003_settings_i18n_bots
Revises: 0002_compat_parity
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_settings_i18n_bots"
down_revision = "0002_user_roles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "localizations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(255), nullable=False),
        sa.Column("locale", sa.String(16), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("category", sa.String(64), nullable=False, server_default="general"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("key", "locale", name="uq_localizations_key_locale"),
    )
    op.create_index("ix_localizations_key", "localizations", ["key"])
    op.create_index("ix_localizations_locale", "localizations", ["locale"])

    op.create_table(
        "platform_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(255), nullable=False, unique=True),
        sa.Column("value_json", sa.JSON(), nullable=True),
        sa.Column("value_type", sa.String(32), nullable=False),
        sa.Column("category", sa.String(64), nullable=False, server_default="general"),
        sa.Column("is_secret", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("editable", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("restart_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_platform_settings_key", "platform_settings", ["key"])

    op.create_table(
        "bot_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bot_key", sa.String(64), nullable=False, unique=True),
        sa.Column("name_key", sa.String(255), nullable=False),
        sa.Column("token_env_key", sa.String(255), nullable=False),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("default_locale", sa.String(16), nullable=False, server_default="en"),
        sa.Column("modules", sa.JSON(), nullable=False),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_bot_profiles_bot_key", "bot_profiles", ["bot_key"])


def downgrade() -> None:
    op.drop_index("ix_bot_profiles_bot_key", table_name="bot_profiles")
    op.drop_table("bot_profiles")
    op.drop_index("ix_platform_settings_key", table_name="platform_settings")
    op.drop_table("platform_settings")
    op.drop_index("ix_localizations_locale", table_name="localizations")
    op.drop_index("ix_localizations_key", table_name="localizations")
    op.drop_table("localizations")
