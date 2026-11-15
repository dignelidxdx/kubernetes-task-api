# Spec: Kubernetes Task API

## Objective

Build a small task-management HTTP API as a progressive Kubernetes learning project. The first implementation will be a FastAPI application with in-memory storage. The project will then evolve through eight explicit versions, each introducing one operational capability without hiding the Kubernetes behavior behind unnecessary abstractions.

The application is intended for local practice with Docker, Minikube, and kubectl before any cloud deployment.

## Scope and Version Roadmap

### Version 1 — FastAPI + in-memory storage

- Implement `GET /health`.
- Implement `GET /tasks`.
- Implement `POST /tasks`.
- Implement `DELETE /tasks/{task_id}`.
- Store tasks in process memory.
- Provide interactive API documentation at `/docs`.
- Run locally with Uvicorn.
- Package the app with Docker and provide a local Kubernetes Deployment and Service to practice three replicas and Pod replacement. The in-memory task list is separate in each Pod.

### Version 2 — Configuration and secrets

- Read non-sensitive settings from environment variables.
- Add a Kubernetes ConfigMap manifest for application configuration.
- Add a Kubernetes Secret manifest containing only development placeholder values.
- Keep real credentials out of Git.

### Version 3 — Container and Kubernetes Deployment

- Refine the initial Docker and Kubernetes setup with versioned image tags and reproducible deployment commands.
- Keep the ClusterIP Service accessible locally through `kubectl port-forward`.

### Version 4 — Replicas and health checks

- Extend the initial three-replica exercise with dedicated readiness and liveness semantics.
- Add tests or demonstrations of probe failures and rolling replacement.
- Compare desired, current, and ready replica counts during a rollout.

### Version 5 — Horizontal scaling

- Define CPU requests and limits.
- Enable Metrics Server in Minikube.
- Add a HorizontalPodAutoscaler.
- Observe scaling behavior under generated load.

### Version 6 — Persistence

- Replace in-memory task storage with a persistence layer.
- Add a Kubernetes PersistentVolumeClaim for local practice.
- Document the limitation that a local PVC is not a production backup strategy.

### Version 7 — Jobs and scheduled backups

- Add a repeatable backup command or script.
- Add a Kubernetes Job manifest for an on-demand backup.
- Add a CronJob manifest for scheduled backups.
- Make backup execution observable through logs and Job status.

### Version 8 — Cloud-ready deployment

- Keep the application image portable.
- Separate environment-specific Kubernetes configuration from application code.
- Document deployment considerations for one selected cloud provider.
- Do not provision or modify cloud resources as part of this initial implementation.

## Tech Stack

- Python 3.12 or the locally available compatible Python 3 version.
- FastAPI.
- Uvicorn.
- Pytest for tests.
- Docker for image packaging from Version 3 onward.
- Kubernetes manifests in YAML.
- Minikube for local Kubernetes practice.

Dependencies should remain minimal. Do not add a database, ORM, migration tool, or cloud SDK before the version that requires it.

## Version 1 Commands

Create an isolated environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

Run the development server:

```powershell
python -m uvicorn app.main:app --reload
```

Run tests:

```powershell
python -m pytest -q
```

## Project Structure

```text
app/
  __init__.py
  main.py
tests/
  test_api.py
requirements.txt
requirements-dev.txt
README.md
Dockerfile
.dockerignore
AGENTS.md
k8s/
  deployment.yaml
  service.yaml
docs/
  specs/
    2026-11-14-kubernetes-task-api.md
```

Version 1 also contains `Dockerfile`, `.dockerignore`, `k8s/deployment.yaml`, and `k8s/service.yaml` for the requested local replica exercise. Future versions may add persistence modules and backup tooling.

## API Contract for Version 1

### `GET /health`

Returns HTTP 200 and a small JSON object indicating that the process is running.

### `GET /tasks`

Returns HTTP 200 and a JSON array of tasks currently held in memory.

### `POST /tasks`

Accepts a JSON body with a required non-empty title and returns the created task with a generated integer ID.

Invalid input returns HTTP 422 using FastAPI validation behavior.

### `DELETE /tasks/{task_id}`

Deletes an existing task and returns HTTP 204. If the ID does not exist, returns HTTP 404.

## Code Style

- Use type annotations for request models, response models, and functions.
- Use Pydantic models for API input and output.
- Keep in-memory state in a small, explicit module.
- Use clear `snake_case` names.
- Avoid global framework magic beyond the FastAPI application instance and the intentionally in-memory store.

Example style:

```python
class TaskCreate(BaseModel):
    title: str = Field(min_length=1)


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> Task:
    task = Task(id=next_id(), title=payload.title, completed=False)
    tasks[task.id] = task
    return task
```

## Testing Strategy

Version 1 must include API tests for:

- Health endpoint success.
- Empty task list.
- Task creation.
- Validation of an empty title.
- Deletion of an existing task.
- 404 for a missing task.

Tests must use an in-process test client and must not require Docker, Minikube, a cloud provider, or network access.

## Boundaries

- Always: keep Version 1 local and minimal; validate request data; run tests before declaring completion; keep real secrets out of the repository; use repository-relative paths in project files.
- Ask first: adding a production database; changing the public API contract; adding authentication; adding cloud resources; adding CI/CD or external services; changing the version roadmap.
- Never: commit credentials; use cloud resources without explicit authorization; remove tests to make a failure pass; add Kubernetes manifests before the corresponding application behavior exists; claim Kubernetes verification without running it.

## Success Criteria for Version 1

- The API starts with the documented Uvicorn command.
- `/docs` is available locally.
- All four endpoints behave according to the API contract.
- The six required API behaviors are covered by passing tests.
- The application has no database or cloud dependency.
- The README explains how to install, run, test, and exercise the API.

## Open Questions

- None required to implement Version 1. The persistence technology for Version 6 remains intentionally undecided until the in-memory and Kubernetes workflow has been completed.
