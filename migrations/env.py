import os
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool

from app import models  # noqa: F401
from app.database import Base


# Загружаем локальные переменные из файла .env.
load_dotenv()

# Alembic предоставляет объект конфигурации для текущего запуска.
config = context.config

# Подключаем настройки журналирования из alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Передаём Alembic описание таблиц из SQLAlchemy-моделей.
target_metadata = Base.metadata


def get_database_url() -> str:
    """
    Возвращает отдельную строку подключения для миграций.

    Мы не используем здесь обычную DATABASE_URL, чтобы случайно
    не запустить миграцию через соединение работающего приложения.
    """
    database_url = os.getenv("MIGRATION_DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "Не задана переменная MIGRATION_DATABASE_URL в файле .env"
        )

    return database_url


def run_migrations_offline() -> None:
    """
    Формирует SQL без непосредственного подключения к базе.

    Этот режим пока не используется, но является стандартной
    возможностью Alembic.
    """
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Подключается к реальной базе и выполняет миграции.
    """
    connectable = create_engine(
        get_database_url(),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=connection.dialect.name == "sqlite",
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()