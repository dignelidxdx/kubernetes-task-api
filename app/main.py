from itertools import count
from socket import gethostname
from threading import Lock

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)


class Task(BaseModel):
    id: int
    title: str
    completed: bool = False


app = FastAPI(title="Kubernetes Task API")
tasks: dict[int, Task] = {}
task_ids = count(1)
store_lock = Lock()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "hostname": gethostname()}


@app.get("/info")
def info() -> dict[str, str]:
    return {"hostname": gethostname()}


@app.get("/tasks", response_model=list[Task])
def list_tasks() -> list[Task]:
    with store_lock:
        return list(tasks.values())


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> Task:
    with store_lock:
        task = Task(id=next(task_ids), title=payload.title)
        tasks[task.id] = task
        return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> Response:
    with store_lock:
        if task_id not in tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        del tasks[task_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
