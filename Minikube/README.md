# Minikube local environment

This folder keeps a local configuration independent from AWS. It uses Docker
`:local` images and in-memory storage; it contains no `DATABASE_URL`,
credentials, RDS endpoints, or ECR references.

## Start the environment

From the project root:

```powershell
minikube start --driver=docker
docker build -t kubernetes-task-api:local .
docker build -t kubernetes-task-frontend:local ./frontend
minikube image load kubernetes-task-api:local
minikube image load kubernetes-task-frontend:local
kubectl apply -f Minikube/
minikube service task-frontend --url
```

The API uses memory in this environment. Tasks are lost when the Pod restarts
or Minikube is deleted. To test real PostgreSQL persistence, use the AWS
deployment and its Secret managed outside Git.

Delete only these resources:

```powershell
kubectl delete -f Minikube/ --ignore-not-found
```
