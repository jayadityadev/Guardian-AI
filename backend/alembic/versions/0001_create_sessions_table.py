"""create sessions table

Revision ID: 0001_create_sessions_table
Revises:
Create Date: 2026-04-29 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0001_create_sessions_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.create_table(
        "sessions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("platform", sa.String(length=50), nullable=False, server_default=sa.text("'json_upload'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("risk_score", sa.Integer(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("grooming_stage", sa.String(length=50), nullable=True),
        sa.Column("recommendation", sa.String(length=50), nullable=True),
        sa.Column("raw_flag_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("drift_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("stage_progression_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("sessions")
