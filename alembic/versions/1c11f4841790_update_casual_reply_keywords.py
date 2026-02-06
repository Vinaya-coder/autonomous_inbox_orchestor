"""Update casual reply keywords

Revision ID: 1c11f4841790
Revises: 5a08383e1210
Create Date: 2026-02-02 17:59:03.163569

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c11f4841790'
down_revision: Union[str, Sequence[str], None] = '17eb4b47b4a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
