from __future__ import annotations

from dataclasses import dataclass
from os import getenv


def storage_backend_name() -> str:
    configured_backend = getenv("STORAGE_BACKEND")
    if configured_backend:
        return configured_backend
    return "postgres" if getenv("DATABASE_URL") else "memory"


@dataclass(frozen=True)
class StoredTask:
    id: int
    title: str
    completed: bool = False


class PostgresTaskStore:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def _connect(self):
        import psycopg

        return psycopg.connect(self.database_url)

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id BIGSERIAL PRIMARY KEY,
                    title TEXT NOT NULL CHECK (length(title) > 0),
                    completed BOOLEAN NOT NULL DEFAULT FALSE
                )
                """
            )

    def list(self) -> list[StoredTask]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, title, completed FROM tasks ORDER BY id"
            ).fetchall()
        return [StoredTask(id=row[0], title=row[1], completed=row[2]) for row in rows]

    def create(self, title: str) -> StoredTask:
        with self._connect() as connection:
            row = connection.execute(
                "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, completed",
                (title,),
            ).fetchone()
        assert row is not None
        return StoredTask(id=row[0], title=row[1], completed=row[2])

    def delete(self, task_id: int) -> bool:
        with self._connect() as connection:
            result = connection.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        return result.rowcount == 1

