"""2026_update_casual_key_words

Revision ID: e2e8fa51e149
Revises: 1c11f4841790
Create Date: 2026-02-03 07:36:15.484195

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2e8fa51e149'
down_revision: Union[str, Sequence[str], None] = '1c11f4841790'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
            INSERT INTO reply_contexts (context_type, keywords, content) VALUES
            (
                'casual',
                'hi,hello,how are you,how is your day,whats up',
                'Hey! I’m doing good 😊 Thanks for asking. How’s your day going?'
            ),
            (
                'casual',
                'hangout,hang out,meet,weekend,fun,cricket',
                'That sounds fun! Let me check my schedule and I’ll get back to you soon 😄'
            ),
            (
                'casual',
                'lunch,team lunch,food,outing',
                'Sounds great! Let me see my availability and I’ll let you know 👍'
            )
    """)



def downgrade() -> None:
    op.execute("""
            DELETE FROM reply_contexts
            WHERE context_type = 'casual'
              AND keywords IN (
                  'hi,hello,how are you,how is your day,whats up',
                  'hangout,hang out,meet,weekend,fun,cricket',
                  'lunch,team lunch,food,outing'
              )
    """)

