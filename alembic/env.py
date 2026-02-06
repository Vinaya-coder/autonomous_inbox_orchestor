from __future__ import with_statement
import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# 1️⃣ Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # email_agent/

# 2️⃣ Import your Base from email_models
from app.database import Base
from app.models.email_models import ChatHistory, Email, EmailLog, ReplyContext # <--- IMPORTANT
# 3️⃣ Load .env.dev for DATABASE_URL
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.dev"))
DATABASE_URL = os.getenv("DATABASE_URL")

# this is the Alembic Config object, which provides access to values within the .ini file
config = context.config

# Override sqlalchemy.url with DATABASE_URL from .env
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# 4️⃣ Set target_metadata for autogenerate
target_metadata = Base.metadata

# 5️⃣ Offline migrations (rarely used)
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# 6️⃣ Online migrations
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# 7️⃣ Run offline or online depending on invocation
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
