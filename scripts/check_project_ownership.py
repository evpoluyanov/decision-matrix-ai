import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool


load_dotenv()

database_url = os.getenv("MIGRATION_DATABASE_URL")

if not database_url:
    raise RuntimeError(
        "Не задана переменная MIGRATION_DATABASE_URL"
    )


engine = create_engine(
    database_url,
    poolclass=NullPool,
)


with engine.connect() as connection:
    users = connection.execute(
        text(
            """
            SELECT
                id,
                email,
                created_at
            FROM users
            ORDER BY id
            """
        )
    ).all()

    projects = connection.execute(
        text(
            """
            SELECT
                id,
                name,
                owner_id
            FROM projects
            ORDER BY id
            """
        )
    ).all()


print()
print("ПОЛЬЗОВАТЕЛИ")
print("-" * 60)

if not users:
    print("Пользователей нет.")

for user in users:
    print(
        f"id={user.id}, "
        f"email={user.email!r}, "
        f"created_at={user.created_at}"
    )


print()
print("ПРОЕКТЫ")
print("-" * 60)

if not projects:
    print("Проектов нет.")

for project in projects:
    print(
        f"id={project.id}, "
        f"name={project.name!r}, "
        f"owner_id={project.owner_id}"
    )


orphan_projects = [
    project
    for project in projects
    if project.owner_id is None
]


print()
print("ИТОГ")
print("-" * 60)
print(f"Пользователей: {len(users)}")
print(f"Проектов: {len(projects)}")
print(
    "Проектов без владельца: "
    f"{len(orphan_projects)}"
)