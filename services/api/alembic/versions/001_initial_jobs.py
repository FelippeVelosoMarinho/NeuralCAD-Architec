"""initial jobs table

Revision ID: 001_initial
Revises:
Create(Date): 2026-05-03

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("payload_json", JSONB, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("artifact_key", sa.String(512), nullable=True),
        sa.Column("dimensional_audit", JSONB, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("jobs")
