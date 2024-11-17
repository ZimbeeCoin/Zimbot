# Import statements at the top
import logging
import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import create_engine, engine_from_config, pool

from alembic import context

# Load environment variables from .env file
load_dotenv()

# Alembic Config object for accessing the .ini file values
config = context.config

# Configure logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

# Import the Base from your models to allow autogenerate to detect schema changes
from src.zimbot.core.models.user import Base  # Adjust path if needed

# Metadata object for 'autogenerate' to detect model changes
target_metadata = Base.metadata

# Retrieve and validate the database URL
database_url = os.getenv("DATABASE_URL")
if not database_url:
    logger.error("DATABASE_URL is not set in the environment.")
    raise ValueError("DATABASE_URL is required for running migrations.")
config.set_main_option("sqlalchemy.url", database_url)

# Optional: additional connection settings for production
CONNECTION_OPTIONS = {
    "pool_size": int(os.getenv("DB_POOL_SIZE", 10)),
    "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", 20)),
    "pool_timeout": int(os.getenv("DB_TIMEOUT", 30)),
    "poolclass": pool.QueuePool,  # Production-optimized connection pool
}


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
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

    Raises:
        Exception: if migration fails
    """
    connectable = create_engine(
        database_url,  # Ensure this is a string, not None
        **CONNECTION_OPTIONS,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            isolation_level="AUTOCOMMIT",  # Customize based on application needs
        )

        try:
            with context.begin_transaction():
                context.run_migrations()
        except Exception as e:
            logger.error("Migration failed: %s", str(e))
            raise  # Log the exception and re-raise it for visibility


# Decide which mode to run: offline or online
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
