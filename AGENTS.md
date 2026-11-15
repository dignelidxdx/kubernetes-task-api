# Project guidance

- Follow `docs/specs/2026-11-14-kubernetes-task-api.md` for the version roadmap.
- Keep changes scoped to the current version and use repository-relative paths in project artifacts.
- Run `python -m pytest -q` when Python and development dependencies are available.
- Keep credentials, local configuration, and generated files out of Git.
- The Kubernetes example intentionally has three replicas to demonstrate reconciliation. The in-memory task lists are independent per Pod until persistence is introduced.
- Do not commit, push, deploy, or change remote services without explicit authorization.
