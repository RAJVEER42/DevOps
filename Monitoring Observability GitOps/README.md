# Monitoring, Observability and GitOps

**Name:** Rajveer Bishnoi
**Enrollment Number:** 24BCS10404

| Folder | Contents |
|---|---|
| [01-monitoring/](01-monitoring/) | A `docker compose` stack: an instrumented app, Prometheus with alert rules, node-exporter, cAdvisor, Grafana with a provisioned dashboard. Request rate, error rate, latency, CPU, memory, alerts |
| [02-observability/](02-observability/) | Metrics, logs and traces explained, how they connect, the tools, and what Kubernetes provides out of the box, exercised on Minikube |
| [03-gitops/](03-gitops/) | Argo CD on Minikube tracking a path in this repository: first sync, change via `git push`, self-heal after manual drift, prune after a deletion |

Everything runs locally. The monitoring stack is Docker Compose on the laptop; the
observability and GitOps parts use the existing Minikube cluster. Argo CD tracks
`Monitoring Observability GitOps/03-gitops/app` on `main` in this very repository, so the
GitOps commits are visible in `git log`.
