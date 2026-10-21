# Issue Tracker: an end-to-end DevOps capstone

**Name:** Rajveer Bishnoi
**Enrollment Number:** 24BCS10404
**Roll Number:** 10404

A three-tier issue tracker — React front end, FastAPI back end, PostgreSQL — taken from a
developer laptop to a monitored Kubernetes deployment. The application is deliberately small so
that the delivery system around it can be the subject: tests, image scanning, a container
registry, Helm, Ingress, autoscaling, probes, Prometheus, Grafana, Argo CD, Terraform, and a
troubleshooting drill with planted faults.

![The issue board running under Docker Compose](Final%20DevOps%20Project/screenshots/app-board.png)

The interface is a triage board. Priority is shown as **acuity** — a ranked numeral, a word and a
colour together, so urgency survives a compressed recording where hue does not — and every issue
carries its time-in-state.

| | |
|---|---|
| Full write-up | [Final DevOps Project/](Final%20DevOps%20Project/README.md) |
| The application | [Issue Tracker Compose/](Issue%20Tracker%20Compose/README.md) |
| Demo deck | [slides.pptx](Final%20DevOps%20Project/demo/slides.pptx) · [PDF](Final%20DevOps%20Project/demo/slides.pdf) |
| Pipeline | [`issue-tracker-cicd.yml`](.github/workflows/issue-tracker-cicd.yml) |
| Reference run | [38892471244](https://github.com/RAJVEER42/DevOps/actions/runs/38892471244) on `17ee1b0`, five jobs green |
| Images | `ghcr.io/rajveer42/issue-tracker-backend:17ee1b0` · `…-frontend:17ee1b0` |

## Contents

[1. Architecture](#1-architecture) · [2. The application](#2-the-application) ·
[3. Run it locally](#3-run-it-locally) · [4. Tests](#4-tests) ·
[5. The pipeline](#5-the-pipeline) · [6. The security gate](#6-the-security-gate) ·
[7. Kubernetes and Helm](#7-kubernetes-and-helm) · [8. Observability](#8-observability) ·
[9. GitOps](#9-gitops) · [10. Troubleshooting drill](#10-troubleshooting-drill) ·
[11. Known issues](#11-known-issues-and-limitations) · [12. Coursework index](#12-coursework-index)

## 1. Architecture

```
developer ── git push ──> GitHub ──> GitHub Actions
                                       ├─ pytest + frontend build
                                       ├─ docker build (backend, frontend)
                                       ├─ Trivy scan, fail on HIGH/CRITICAL with a fix
                                       ├─ push ghcr.io/rajveer42/issue-tracker-{backend,frontend}:<sha>
                                       └─ helm upgrade --install on a kind cluster + smoke test
                     │
                     └──────────────> Argo CD (in the cluster) watches helm/issue-tracker on main
                                                         │ sync
   browser ──> Ingress (nginx) ──┬── /     ──> frontend Service ──> nginx Pods
     tracker.local               └── /api  ──> backend  Service ──> FastAPI Pods (2..5, HPA)
                                                                        │
                                                      Prometheus scrapes /metrics ──> Grafana
                                                                        │
                                                            postgres StatefulSet + PVC
```

The Ingress is the only way in: postgres has no Service exposed outside the namespace and no
NodePort.

## 2. The application

An issue has a title, a priority and an optional assignee, and moves through `open` →
`in_progress` → `done`. Nine endpoints, three of them operational:

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness. Answers from the process alone, touches no dependency. |
| `GET` | `/ready` | Readiness. Executes a query, so a database problem removes the Pod from the Service. |
| `GET` | `/metrics` | Prometheus exposition. |
| `GET` | `/api/issues` | List, filterable by status. |
| `GET` | `/api/issues/stats` | Counts by status and priority, plus open-and-high. |
| `GET` | `/api/issues/{id}` | Fetch one. |
| `POST` | `/api/issues` | Create. Rejects a priority outside low/medium/high. |
| `PUT` | `/api/issues/{id}` | Update. |
| `DELETE` | `/api/issues/{id}` | Delete. |

The split between `/health` and `/ready` is the part worth explaining. A liveness probe that
queried the database would restart a healthy Pod every time the database blinked. `/ready` is the
one that checks it, so the Pod leaves the Service instead of being killed — which is exactly what
turned a bad config change into a stuck rollout rather than an outage in [§10](#10-troubleshooting-drill).

The board is responsive; the same screen stacks on a phone.

<img src="Final%20DevOps%20Project/screenshots/app-board-mobile.png" alt="The board at phone width" width="320">

## 3. Run it locally

```bash
cd "Issue Tracker Compose"
docker compose up -d --build
open http://localhost:8080
```

Three services. `postgres` must report healthy before the backend starts, because the backend runs
its Alembic migrations immediately. The frontend's nginx proxies `/api` to the backend, so the
browser only ever talks to port 8080 and there is no CORS layer anywhere.

## 4. Tests

Eight pytest cases run against a real FastAPI app with a SQLite session per test: the full
create/read/update/delete cycle, rejection of an invalid priority, listing and filtering, the stats
aggregation, readiness actually hitting the database, and the metrics counter incrementing when an
issue is created.

![pytest passing](Issue%20Tracker%20Compose/screenshots/tests.png)

Tests are the first job in the pipeline, so a red test can never produce a pushed tag.

## 5. The pipeline

Three stages, and nothing reaches the registry until the tests and the scanner both agree.

![The pipeline run](Final%20DevOps%20Project/screenshots/ci-run.png)

1. **backend tests** (pytest, JUnit artifact) and **frontend build** (Vite, `dist` artifact), in parallel.
2. **images**, a matrix over `backend` and `frontend`: buildx with a per-service cache, a Trivy
   scan with its JSON report kept as an artifact, then a push to GHCR tagged with the git SHA.
   Pull requests stop before the push.
3. **deploy**: a kind cluster inside the runner, a pull secret minted from the run's own token,
   `helm upgrade --install` with the tag just pushed, then a smoke test from inside the cluster.

The smoke test is what makes the job meaningful. It does not merely check that the release
installed; it creates an issue through nginx, reads the stats back, and asserts the metrics
counter moved — exercising nginx, the backend and postgres in one pass.

![Job log excerpts: tests, both scans, the pushes, the smoke test](Final%20DevOps%20Project/screenshots/ci-jobs.png)

The DevSecOps pipeline for the companion service runs the longer gate — SAST, SCA, secret
scanning and image scanning before a security gate decides whether to push.

![DevSecOps pipeline, nine jobs green](DevSecOps%20Pipeline/screenshots/actions-run.png)

## 6. The security gate

```
severity:        HIGH,CRITICAL
ignore-unfixed:  true      # no patch available anywhere: report, do not block
exit-code:       1         # anything else fails the job before the push
```

A vulnerability that clears with a version bump should block the build, because the fix is cheap.
One with no fix anywhere should be visible but must not freeze every release — a gate that blocks
on things nobody can fix is a gate people switch off.

The scanner failed the build twice before it passed, both times in dependencies rather than
project code: the frontend's Alpine base was behind (fixed by moving to
`nginxinc/nginx-unprivileged:1.29-alpine` with `apk upgrade`, which also bought a non-root
default), then Starlette under FastAPI, which the pinned FastAPI would not let pip upgrade past
(fixed by `fastapi==0.142.2` with `starlette==1.7.0` pinned explicitly). Both fixes are in the
committed image and dependency definitions.

![Local Trivy scan of both images, same policy as CI](Final%20DevOps%20Project/screenshots/trivy-local.png)

Layer-by-layer controls are listed in
[Final DevOps Project/security/](Final%20DevOps%20Project/security/README.md).

## 7. Kubernetes and Helm

One chart creates the whole release: a postgres StatefulSet with a `volumeClaimTemplate`, a
backend with startup, readiness and liveness probes running as non-root with capabilities
dropped, an nginx frontend, an Ingress, and an HPA holding the backend between 2 and 5 replicas.

![helm upgrade --install and the resulting objects](Final%20DevOps%20Project/screenshots/helm-deploy.png)

The backend Deployment carries a `checksum/config` annotation computed from the ConfigMap and
Secret, so a configuration change rolls the Pods. Without it, a config change updates the objects
and nothing restarts to pick it up — invisible until it bites.

| Verified in the cluster | The board, running on Kubernetes |
|---|---|
| ![API, metrics and persistence verified in the cluster](Final%20DevOps%20Project/screenshots/verify-in-cluster.png) | ![The board running on Kubernetes](Final%20DevOps%20Project/screenshots/app-on-kubernetes.png) |

Persistence was verified by deleting the postgres Pod: the StatefulSet recreated it against the
same PVC and the existing issues were still there.

## 8. Observability

Prometheus discovers backend Pods by annotation, so a Pod the autoscaler adds is scraped within
one interval with no edit to the scrape config. The autoscaler and the monitoring are designed
together: neither needs to know how many replicas there will be.

| Prometheus targets | Under load, with the HPA scaling |
|---|---|
| ![Every backend Pod discovered and up](Final%20DevOps%20Project/screenshots/prometheus-targets.png) | ![The autoscaler reacting to load](Final%20DevOps%20Project/screenshots/monitoring-and-hpa.png) |

The application exposes a request counter by route and status, a latency histogram, an in-flight
gauge, and a counter of issues created — a business signal rather than an infrastructure one, and
the one the CI smoke test asserts against.

![The provisioned Grafana dashboard](Final%20DevOps%20Project/screenshots/grafana-dashboard.png)

Two alert rules back it up, because a dashboard nobody is watching catches nothing:
`BackendHighErrorRate` (5xx above five percent for two minutes) and `BackendDown`.

## 9. GitOps

An Argo CD `Application` tracks the chart on `main` with automated sync, prune and self-heal.
Change a value, commit, push; nobody runs `helm` by hand.

The lesson from that run was about ownership of the replica count:

```yaml
ignoreDifferences:
  - group: apps
    kind: Deployment
    name: tracker-backend      # scoped, not blanket
    jsonPointers: [/spec/replicas]
```

The first version applied `ignoreDifferences` to *every* Deployment, so Argo CD also ignored a
deliberate change to the frontend's replica count. GitOps and an autoscaler disagree about who
owns `spec.replicas`; the conflict has to be declared, and declared for the right object.

## 10. Troubleshooting drill

Two faults introduced into the running release, each diagnosed from the cluster before any fix was
applied.

| Fault | Symptom | Found with | Fix |
|---|---|---|---|
| Wrong database host via a values override | Rollout stuck, new Pod `0/1`, old Pods still serving | `kubectl logs` (name resolution), `describe` probe events | `helm rollback tracker` |
| Ingress `/api` to a Service that does not exist | UI loads, every API call returns `503` | `describe ingress` names the missing Service | Re-render the chart's Ingress |

| Fault 1 | Fault 2 |
|---|---|
| ![The stuck rollout](Final%20DevOps%20Project/troubleshooting/fault-1.png) | ![503 through the Ingress](Final%20DevOps%20Project/troubleshooting/fault-2.png) |

The first fault is why the probes are shaped the way they are: because readiness checks the
database, the new Pod never became Ready, the rolling update refused to proceed, and the old Pods
kept serving. A bad configuration change became a stuck rollout instead of an outage.

## 11. Known issues and limitations

- **EKS was not created.** This ran on Minikube. A real EKS control plane plus nodes and a NAT
  gateway costs money per session and no AWS account was available. The VPC project in
  [Cloud Terraform](Cloud%20Terraform/02-vpc-project/) builds the network it would sit in; adding
  the cluster is one `module "eks"` block pointed at those subnets, plus
  `aws eks update-kubeconfig` and the same `helm upgrade --install` used here.
- **Terraform ran against LocalStack**, not real AWS. One variable (`use_localstack`) switches the
  provider; nothing else in the configuration changes.
- **`tracker.local` needs a hosts entry** for the Ingress checks, and the HPA needs
  metrics-server enabled on Minikube.
- **A few screenshots elsewhere in this repository still need retaking.** The CI, shell, container
  and application captures have been regenerated from runs on this account and this machine; a
  small number of Argo CD and cluster captures have not, and are not embedded above.

## 12. Coursework index

The topics leading up to the capstone. Each folder has its own README with the commands that were
run, their output, and screenshots from the run.

| Folder | Topic |
|---|---|
| `Linux Fundamentals/` | Hard vs soft links, `useradd` vs `adduser`, `journalctl`, command cheat sheet |
| `Shell Scripting/` | `sysinfo.sh`: variables, user input, `mkdir`/`touch`, output redirection |
| `Networking Fundamentals/` | `ping`, `ip`, `ss`, `curl`, `wget`, `nslookup`, `traceroute`, `hostname` |
| `Git and Github/` | `git commit -a` vs `-m`, `git cherry-pick` |
| `Docker Fundamentals/` | Six Hello World containers: Node.js, Python, Java, Apache, React, Nginx |
| `DockerFiles and Images/` | Multi-stage Go build, 365 MB toolchain to a 7 MB image |
| `Docker Networks/` | Multi-network containers, host network, bind mounts, overlay networks |
| `Kubernetes Fundamentals/` | Minikube setup, cluster architecture, core objects, the Kubernetes Basics tutorial |
| `Kubernetes Workloads/` | Rolling update, blue-green, canary and recreate strategies; the twelve-state Pod lifecycle lab |
| `Kubernetes Services/` | The five Service types, object comparisons, FQDN and CoreDNS notes |
| `Kubernetes Ingress ConfigMaps Secrets/` | ConfigMap and Secret injection, path-based Ingress, troubleshooting, Ingress vs controller |
| `Kubernetes Events and Logs/` | What events and logs each are, who writes them, and when to read which |
| `Kubernetes Troubleshooting/` | The kubectl diagnostic commands, nine broken-and-fixed scenarios, a mini project |
| `Kubernetes Storage HPA Probes/` | emptyDir, hostPath, PV/PVC, StorageClass; HPA under load; a probes-plus-PVC mini project |
| `Helm/` | Helm command tour, upgrade and rollback cycle, a chart with dev and prod value files |
| `CI-CD Pipeline/` | GitHub Actions: lint, matrix tests, image publish to GHCR, smoke test of the published image |
| `DevSecOps Pipeline/` | Build, test, SAST, SCA, secret scan, image scan, security gate, push, deploy to kind |
| `Terraform Basics/` | Infrastructure as code, an S3 project run end to end, notes on IAM, EC2, S3, VPC, DynamoDB and RDS |
| `Cloud Terraform/` | Cloud fundamentals and a Terraform VPC project: subnets, gateway, routes, security group, optional EC2 |
| `Issue Tracker Compose/` | The application itself: FastAPI, React and PostgreSQL with Dockerfiles and Compose |
| `Monitoring Observability GitOps/` | Prometheus and Grafana with alerts, the three observability signals, an Argo CD demo |
| `Final DevOps Project/` | The capstone: Helm chart, CI with Trivy and GHCR, Prometheus and Grafana in-cluster, Argo CD, troubleshooting |

Environment: macOS with Docker Desktop; Linux-only commands were run in Ubuntu 24.04 containers.
The Kubernetes work used Minikube with the Docker driver. The pipelines run on GitHub Actions;
their workflow files are in `.github/workflows/`. The Terraform projects ran against LocalStack
and switch to real AWS with one variable.
