"""Add 3 new reply contexts

Revision ID: 17eb4b47b4a8
Revises: 6a7a4d672323
Create Date: 2026-02-02 14:41:02.842172

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17eb4b47b4a8'
down_revision: Union[str, Sequence[str], None] = '6a7a4d672323'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
            INSERT INTO reply_contexts (context_type, keywords, content)
            VALUES (
                'casual',
                'friend,hi,hello,how are you',
                'Vinaya enjoys friendly chats, cricket, hanging out with friends, and replying naturally to casual messages.'
            )
        """)



def downgrade() -> None:
    op.execute("""
            DELETE FROM reply_contexts
            WHERE context_type='casual'
            AND keywords='friend,hi,hello,how are you'
        """)
