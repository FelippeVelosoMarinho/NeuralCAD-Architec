"""add celery_task_id for revoke on cancel

Revision ID: 002_celery
Revises: 001_initial
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_celery"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("celery_task_id", sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column("jobs", "celery_task_id")
