from app.storage import PostgresTaskStore, StoredTask, storage_backend_name


class FakeResult:
    def __init__(self, rows=(), rowcount=0):
        self.rows = list(rows)
        self.rowcount = rowcount

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.rows[0] if self.rows else None


class FakeConnection:
    def __init__(self):
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, query, params=None):
        self.calls.append((" ".join(query.split()), params))
        if query.lstrip().startswith("SELECT"):
            return FakeResult([(1, "persisted task", False)])
        if query.lstrip().startswith("INSERT"):
            return FakeResult([(2, "new task", False)])
        if query.lstrip().startswith("DELETE"):
            return FakeResult(rowcount=1)
        return FakeResult()


def test_storage_backend_name_follows_database_url(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert storage_backend_name() == "memory"

    monkeypatch.setenv("DATABASE_URL", "postgresql://test")
    assert storage_backend_name() == "postgres"


def test_storage_backend_can_be_selected_explicitly(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("STORAGE_BACKEND", "postgres")
    assert storage_backend_name() == "postgres"

    monkeypatch.setenv("STORAGE_BACKEND", "memory")
    assert storage_backend_name() == "memory"


def test_postgres_store_list_create_and_delete_use_parameterized_queries() -> None:
    connection = FakeConnection()
    store = PostgresTaskStore("postgresql://test")
    store._connect = lambda: connection

    assert store.list() == [StoredTask(1, "persisted task", False)]
    assert store.create("new task") == StoredTask(2, "new task", False)
    assert store.delete(2) is True

    assert connection.calls == [
        ("SELECT id, title, completed FROM tasks ORDER BY id", None),
        (
            "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, completed",
            ("new task",),
        ),
        ("DELETE FROM tasks WHERE id = %s", (2,)),
    ]


def test_postgres_store_initialize_creates_expected_table() -> None:
    connection = FakeConnection()
    store = PostgresTaskStore("postgresql://test")
    store._connect = lambda: connection

    store.initialize()

    query, params = connection.calls[0]
    assert params is None
    assert "CREATE TABLE IF NOT EXISTS tasks" in query
    assert "title TEXT NOT NULL" in query
    assert "completed BOOLEAN NOT NULL DEFAULT FALSE" in query
