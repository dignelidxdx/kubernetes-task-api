from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert isinstance(body["hostname"], str)
    assert body["hostname"]


def test_info_includes_hostname() -> None:
    response = client.get("/info")
    assert response.status_code == 200
    assert response.json()["hostname"]


def test_task_lifecycle() -> None:
    assert client.get("/tasks").json() == []

    created = client.post("/tasks", json={"title": "Learn Kubernetes"})
    assert created.status_code == 201
    task = created.json()
    assert task == {"id": 1, "title": "Learn Kubernetes", "completed": False}
    assert client.get("/tasks").json() == [task]

    assert client.delete("/tasks/1").status_code == 204
    assert client.get("/tasks").json() == []
    assert client.delete("/tasks/1").status_code == 404


def test_empty_title_is_rejected() -> None:
    assert client.post("/tasks", json={"title": ""}).status_code == 422
