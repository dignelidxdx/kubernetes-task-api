import os

from fastapi.testclient import TestClient

# API tests must remain local and deterministic even when a developer has a
# DATABASE_URL configured for an integration environment.
os.environ.pop("DATABASE_URL", None)

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body == {"status": "ok"}


def test_info_includes_hostname() -> None:
    response = client.get("/info")
    assert response.status_code == 200
    assert response.json()["hostname"]


def test_task_lifecycle() -> None:
    default_tasks = client.get("/tasks").json()
    assert default_tasks
    next_id = max(task["id"] for task in default_tasks) + 1

    created = client.post("/tasks", json={"title": "Learn Kubernetes"})
    assert created.status_code == 201
    task = created.json()
    assert task == {"id": next_id, "title": "Learn Kubernetes", "completed": False}
    assert client.get("/tasks").json()[-1] == task

    assert client.delete(f"/tasks/{next_id}").status_code == 204
    assert task not in client.get("/tasks").json()
    assert client.delete(f"/tasks/{next_id}").status_code == 404


def test_tasks_allow_frontend_origin() -> None:
    response = client.get("/tasks", headers={"Origin": "http://localhost:8080"})
    assert response.headers["access-control-allow-origin"] == "http://localhost:8080"


def test_empty_title_is_rejected() -> None:
    assert client.post("/tasks", json={"title": ""}).status_code == 422


def test_database_url_is_supported_by_application_configuration() -> None:
    from app.storage import storage_backend_name

    assert storage_backend_name() in {"memory", "postgres"}
