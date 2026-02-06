"""Add fallback context for out-of-context emails

Revision ID: 6a7a4d672323
Revises: 928d6bc359b8
Create Date: 2026-02-02 14:14:56.217322

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a7a4d672323'
down_revision: Union[str, Sequence[str], None] = '928d6bc359b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
