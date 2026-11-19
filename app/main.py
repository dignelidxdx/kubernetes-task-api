from itertools import count
from os import getenv
from socket import gethostname
from threading import Lock

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.storage import PostgresTaskStore, StoredTask, storage_backend_name


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)


class Task(BaseModel):
    id: int
    title: str
    completed: bool = False


allowed_origins = [
    origin.strip()
    for origin in getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
if not allowed_origins:
    allowed_origins = ["http://localhost:8080"]


app = FastAPI(title="Kubernetes Task API", root_path=getenv("ROOT_PATH", ""))
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

default_tasks: dict[int, Task] = {
    1: Task(id=1, title="Explore the API documentation"),
    2: Task(id=2, title="Query tasks from the frontend"),
    3: Task(id=3, title="Practice Docker Compose"),
}
tasks: dict[int, Task] = dict(default_tasks)
task_ids = count(max(tasks) + 1)
store_lock = Lock()
postgres_store = (
    PostgresTaskStore(getenv("DATABASE_URL")) if storage_backend_name() == "postgres" else None
)



def as_task(stored: StoredTask) -> Task:
    return Task(id=stored.id, title=stored.title, completed=stored.completed)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/info")
def info() -> dict[str, str]:
    return {"hostname": gethostname()}


@app.get("/tasks", response_model=list[Task])
def list_tasks() -> list[Task]:
    if postgres_store is not None:
        return [as_task(task) for task in postgres_store.list()]
    with store_lock:
        return list(tasks.values())


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> Task:
    if postgres_store is not None:
        return as_task(postgres_store.create(payload.title))
    with store_lock:
        task = Task(id=next(task_ids), title=payload.title)
        tasks[task.id] = task
        return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> Response:
    if postgres_store is not None:
        if not postgres_store.delete(task_id):
            raise HTTPException(status_code=404, detail="Task not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    with store_lock:
        if task_id not in tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        del tasks[task_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
