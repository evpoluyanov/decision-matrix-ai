import io

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

from app import models
from app.database import Base


def test_upgrade_downgrade_upgrade_preserves_existing_users_and_logs(tmp_path, monkeypatch):
    url = f'sqlite:///{tmp_path / "migration.db"}'
    monkeypatch.setenv("MIGRATION_DATABASE_URL", url)
    config = Config("alembic.ini")
    command.upgrade(config, "89b807e95fe4")
    engine = create_engine(url)
    with Session(engine) as db:
        user = models.User(email="keep@example.com", password_hash="keep", email_verified=True)
        db.add(user)
        db.flush()
        db.add(models.AIRequestLog(user_id=user.id, project_id=123, feature="alternatives",
                                  status="completed", total_tokens=250))
        db.commit()
    command.upgrade(config, "head")
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT total_tokens FROM ai_request_logs")) == 250
        assert connection.scalar(text("SELECT email_verified FROM users")) == 1
        differences = compare_metadata(MigrationContext.configure(connection, opts={"compare_type": True}), Base.metadata)
        assert differences == []
    command.downgrade(config, "89b807e95fe4")
    assert "ai_provider_calls" not in inspect(engine).get_table_names()
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT total_tokens FROM ai_request_logs")) == 250
    command.upgrade(config, "head")
    assert "ai_daily_budgets" in inspect(engine).get_table_names()
    assert "ai_score_generation_jobs" in inspect(engine).get_table_names()
    engine.dispose()


def test_postgresql_migration_sql_is_additive_and_preserves_ledger_fk(monkeypatch):
    # Offline SQL only. No actual PostgreSQL connection or production credentials.
    monkeypatch.setenv("MIGRATION_DATABASE_URL", "postgresql+psycopg://unused:unused@localhost/unused")
    output = io.StringIO()
    config = Config("alembic.ini", output_buffer=output)
    command.upgrade(config, "89b807e95fe4:c9a7f431b2d0", sql=True)
    sql = output.getvalue()
    assert "CREATE TABLE ai_daily_budgets" in sql
    assert "CREATE TABLE auth_rate_limits" in sql
    assert "CREATE TABLE ai_provider_calls" in sql
    assert "ON DELETE SET NULL" in sql
    assert "DROP TABLE" not in sql
    assert "ALTER TABLE users" not in sql


def test_score_generation_migration_is_additive_in_postgresql(monkeypatch):
    # Offline SQL only. No actual PostgreSQL connection or production credentials.
    monkeypatch.setenv(
        "MIGRATION_DATABASE_URL",
        "postgresql+psycopg://unused:unused@localhost/unused",
    )
    output = io.StringIO()
    config = Config("alembic.ini", output_buffer=output)
    command.upgrade(config, "c9a7f431b2d0:6f3a1c9e2b70", sql=True)
    sql = output.getvalue()
    assert "CREATE TABLE ai_score_generation_jobs" in sql
    assert "FOREIGN KEY(project_id)" in sql
    assert "FOREIGN KEY(request_log_id)" in sql
    assert "ON DELETE CASCADE" in sql
    assert "DROP TABLE" not in sql
