import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# This is the crucial part:
# 1. Add the project's root directory to the Python path.
# This ensures that Alembic can find your other modules like 'models' and 'config'.
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

# 2. Import your settings and your SQLAlchemy Base model.
import config
import models


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
alembic_config = context.config

# 3. Set the SQLAlchemy URL from your settings object.
# This makes sure Alembic uses the same database connection string
# as your main FastAPI application, loaded from your .env file.
alembic_config.set_main_option("sqlalchemy.url", config.settings.database_url)


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = models.Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = alembic_config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        alembic_config.get_section(alembic_config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

