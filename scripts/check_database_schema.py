import os

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from app import models  # noqa: F401
from app.database import Base


load_dotenv()

database_url = os.getenv("MIGRATION_DATABASE_URL")

if not database_url:
    raise RuntimeError(
        "В файле .env отсутствует MIGRATION_DATABASE_URL"
    )

print("Подключаемся к Supabase...")
print("Сравниваем реальные таблицы с SQLAlchemy-моделями...")

engine = create_engine(
    database_url,
    poolclass=NullPool,
)

try:
    with engine.connect() as connection:
        migration_context = MigrationContext.configure(
            connection,
            opts={
                "compare_type": True,
            },
        )

        differences = compare_metadata(
            migration_context,
            Base.metadata,
        )
finally:
    engine.dispose()

if differences:
    print()
    print("Обнаружены различия:")

    for difference in differences:
        print(f"- {difference}")

    raise SystemExit(1)

print()
print("Структура Supabase соответствует SQLAlchemy-моделям.")
print("Данные и структура базы не изменялись.")