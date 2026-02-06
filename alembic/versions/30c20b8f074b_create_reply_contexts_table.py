from alembic import op

# revision identifiers
revision = '30c20b8f074b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO reply_contexts (context_type, keywords, content) VALUES
        ('personal', 'my hobbies and my personality', 'I am a cricket lover, I love watching cricket and hanging out with friends. I have completed my graduation in 2025 and am working as an intern in Imaginnovate company located in Vizag. I\'m very friendly and happy with my friends and enjoy being around them. I enjoy reading tech blogs, playing chess, and exploring AI research. I would never say no to my friends.'),
        ('project', 'status', 'The Email Auto-Reply Agent is working fine, all modules are functional.'),
        ('project','status,progress','The Email Auto-Reply Agent is fully functional. Modules for reading emails, generating replies, and logging are working properly.'),
        ('project', 'features,capabilities', 'The agent can read unread emails, generate AI or template replies, send emails, and log all interactions in the database.')
    """)


def downgrade() -> None:
    op.execute("""
        DELETE FROM reply_contexts
        WHERE content IN (
            'I am a cricket lover, I love watching cricket and hanging out with friends. I have completed my graduation in 2025 and am working as an intern in Imaginnovate company located in Vizag. I\'m very friendly and happy with my friends and enjoy being around them. I enjoy reading tech blogs, playing chess, and exploring AI research. I would never say no to my friends.',
            'The Email Auto-Reply Agent is working fine, all modules are functional.',
            'The Email Auto-Reply Agent is fully functional. Modules for reading emails, generating replies, and logging are working properly.',
            'The agent can read unread emails, generate AI or template replies, send emails, and log all interactions in the database.'
        );
    """)
