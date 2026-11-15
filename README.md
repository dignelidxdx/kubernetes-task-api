# Kubernetes Task API

A small FastAPI task API for learning Kubernetes locally. The current version stores tasks in each process's memory. It provides a three-replica Deployment so you can observe Kubernetes replacing a deleted Pod.

## Run locally

Requires Python 3.12 or a compatible Python 3 version.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs` to try `GET /health`, `GET /tasks`, `POST /tasks`, and `DELETE /tasks/{task_id}`. Run tests with `python -m pytest -q`.

## Docker

```powershell
docker build -t kubernetes-task-api:local .
docker run --rm -p 8000:8000 kubernetes-task-api:local
```

Open `http://localhost:8000/docs`. Stop the container with Ctrl+C.

## Kubernetes with Minikube

Requires Docker, Minikube, and kubectl. Start Minikube and load the image built above into its image store:

```powershell
minikube start --driver=docker
docker build -t kubernetes-task-api:local .
minikube image load kubernetes-task-api:local
kubectl apply -f k8s/
kubectl rollout status deployment/task-api
kubectl get deployment,replicaset,pods -l app=task-api
```

Open the API through the local Service:

```powershell
kubectl port-forward service/task-api 8000:80
```

Then open `http://localhost:8000/docs`. Use another terminal for the commands below. Stop port forwarding with Ctrl+C.

To observe reconciliation, copy an actual Pod name from `kubectl get pods -l app=task-api`, then run:

```powershell
kubectl delete pod POD_NAME
kubectl get pods -l app=task-api -w
```

The ReplicaSet creates a replacement to return to three Pods. `DESIRED` is the requested count, `CURRENT` is how many Pods the ReplicaSet has created, and `READY` is how many are ready to serve.

**Memory limitation:** each replica owns its own task list. Requests routed to different Pods can show different tasks; deleting a Pod loses its tasks. Use the three-replica setup to study reconciliation and `/health`. For consistent task operations during this first version, run locally with Uvicorn or Docker, or temporarily scale the Deployment to one replica:

```powershell
kubectl scale deployment/task-api --replicas=1
```

Restore the exercise with `kubectl scale deployment/task-api --replicas=3`. Shared persistence is planned for Version 6.

The complete progression from Version 1 to Version 8 is in [the project specification](docs/specs/2026-11-14-kubernetes-task-api.md).
