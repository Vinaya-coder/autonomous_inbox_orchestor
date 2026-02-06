"""Add sender_email to reply_contexts

Revision ID: 928d6bc359b8
Revises: 30c20b8f074b
Create Date: 2026-02-02 13:58:51.897219

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '928d6bc359b8'
down_revision: Union[str, Sequence[str], None] = '30c20b8f074b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
            INSERT INTO reply_contexts (context_type, keywords, content, sender_email)
            VALUES ('fallback', '', 'Thank you for your email. Could you please clarify or provide more details?', NULL)
        """)

def downgrade() -> None:
    op.execute("""
        DELETE FROM reply_contexts
        WHERE context_type='fallback' AND keywords='' 
          AND content='Thank you for your email. Could you please clarify or provide more details?'
    """)