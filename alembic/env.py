from logging.config import fileConfig
from alembic import context
from sqlalchemy import pool, engine_from_config
from app.mail.database.models_mail import Base
from app.asyncdb import asyncpg_url


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_db_url():
    try:
        return asyncpg_url("DB_MAIL").unicode_string()
    except Exception as e:
        raise RuntimeError(f"Failed to get database URL: {e}")


def run_migrations_offline() -> None:
    url = get_db_url()
    context.configure(
        url=url.replace("+asyncpg", ""),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    url = get_db_url().replace("+asyncpg", "")

    sync_engine = engine_from_config(
        {"sqlalchemy.url": url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with sync_engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
