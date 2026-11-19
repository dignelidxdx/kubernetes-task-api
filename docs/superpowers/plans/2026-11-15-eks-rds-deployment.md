# EKS RDS Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Adapt the task application for EKS with ECR images and Amazon RDS PostgreSQL, while preserving previous Minikube variants as practice material.

**Architecture:** FastAPI will persist tasks in PostgreSQL through a small repository layer. EKS will run backend and frontend Deployments with internal Services; an initialization Job will create the schema in RDS. HPA manifests will target both workloads and require Metrics Server.

**Tech Stack:** FastAPI, psycopg, PostgreSQL, Docker, Kubernetes, eksctl, Amazon ECR, Amazon RDS.

**Spec:** `docs/superpowers/specs/2026-11-15-eks-rds-deployment-design.md`

## Global Constraints

- Keep real credentials out of Git.
- Use repository-relative paths in project artifacts.
- Do not create, delete, or modify AWS resources during local implementation.
- Preserve practice manifests under `k8s/practice/`.
- Keep the application API contract unchanged.
- Use idempotent database initialization.

## Review Focus

- Missing or invalid `DATABASE_URL` must produce a clear startup/health failure.
- Database initialization must be safe to run more than once.
- Task creation, listing, and deletion must remain compatible with the existing API.
- EKS Deployments must not reference local-only images or `imagePullPolicy: Never`.
- HPA manifests must define resource requests and document the Metrics Server dependency.

### Task 1: Reorganize Kubernetes practice and active manifests

**Files:**
- Move: existing Minikube/practice variants into `k8s/practice/`
- Modify: `README.md`
- Modify: `k8s/` active manifests

- [ ] Inventory existing manifests and classify local practice versus active EKS resources.
- [ ] Move only obsolete/local variants into `k8s/practice/` without changing their behavior.
- [ ] Update README commands so the main workflow cannot accidentally apply practice variants.
- [ ] Verify all referenced paths in README exist.

### Task 2: Add PostgreSQL persistence to the backend

**Files:**
- Modify: `requirements.txt`
- Create: `app/db.py`
- Modify: `app/main.py`
- Modify: `tests/test_api.py`

**Interfaces:**
- `app/db.py` provides connection setup and task CRUD operations using `DATABASE_URL`.
- `app/main.py` keeps the existing `/health`, `/info`, `/tasks`, and `/tasks/{task_id}` routes.

- [ ] Add the minimal PostgreSQL driver dependency.
- [ ] Add tests for task list, create, delete, missing database configuration, and database-backed behavior.
- [ ] Implement the repository with parameterized SQL and transaction boundaries.
- [ ] Preserve the existing response models and status codes.
- [ ] Run `python -m pytest -q`.

### Task 3: Add database initialization and secret templates

**Files:**
- Create: `db/init.sql`
- Create: `k8s/db-init-job.yaml`
- Create: `k8s/secret.example.yaml`
- Modify: `k8s/auth-config.yaml`
- Modify: `README.md`

- [ ] Define the `tasks` table and indexes required by the API in `db/init.sql`.
- [ ] Make the SQL idempotent with `CREATE TABLE IF NOT EXISTS` and safe seed data.
- [ ] Define a `db-init` Job that reads `DATABASE_URL` from `task-api-db` and runs the SQL.
- [ ] Keep the example Secret free of real passwords and document the imperative creation command.
- [ ] Document that the Job must run after RDS is reachable and before the backend rollout.

### Task 4: Adapt backend and frontend manifests for EKS

**Files:**
- Modify: `k8s/deployment.yaml`
- Modify: `k8s/frontend/deployment.yaml`
- Modify: `k8s/service.yaml`
- Modify: `k8s/frontend/service.yaml`
- Create: `k8s/hpa.yaml`

- [ ] Replace local image names with documented ECR image placeholders and use `IfNotPresent`.
- [ ] Inject `DATABASE_URL` from `task-api-db` into the backend.
- [ ] Add CPU and memory requests/limits required by HPA.
- [ ] Add HPA resources for backend and frontend with conservative learning defaults.
- [ ] Keep Services simple and document that public exposure is a later networking step without Ingress.
- [ ] Validate manifests with a YAML parser and `kubectl apply --dry-run=client` when available.

### Task 5: Prepare EKS/RDS operating documentation

**Files:**
- Modify: `k8s/eks/simple-cluster.yaml`
- Create: `docs/eks-rds-deployment.md`
- Modify: `README.md`

- [ ] Document the existing EKS cluster and managed node group configuration.
- [ ] Document the RDS prerequisites: subnet/security-group reachability, database endpoint, port, and credentials.
- [ ] Document ECR build/tag/push commands without embedding account credentials.
- [ ] Document the apply order: Secret, `db-init`, backend/frontend, Services, HPA.
- [ ] Document verification and cleanup commands, clearly distinguishing local practice from AWS resources.

### Task 6: Verification and handoff

- [ ] Run backend tests.
- [ ] Build both Docker images locally.
- [ ] Validate manifests without contacting AWS.
- [ ] Search changed artifacts for local absolute paths, credentials, and personal environment details.
- [ ] Report remaining AWS-only steps that require explicit user execution and authorization.

