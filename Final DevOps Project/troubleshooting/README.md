# Troubleshooting challenge

Two faults introduced into a working release, each diagnosed with commands before any YAML
was touched. The method is the one from [Kubernetes Troubleshooting](../../Kubernetes%20Troubleshooting/):
status, then events, then logs, then the path.

## Fault 1: backend cannot reach the database

`fault-1-wrong-db-host.yaml` is a Helm values override that sets the ConfigMap's `POSTGRES_HOST`
to a Service that does not exist.

**Symptom.** After `helm upgrade -f fault-1-wrong-db-host.yaml`, new backend Pods never become
Ready; the rollout stalls; the old Pods keep serving (rolling update protects users).
**Investigation.** `kubectl get pods` shows the new ReplicaSet's Pods `0/1` with restarts;
`kubectl logs` shows Alembic failing to resolve `tracker-postgres-typo`; `kubectl get svc`
lists the real name; `kubectl get configmap tracker-config -o yaml` shows the bad value.
**Root cause.** Wrong hostname in configuration. DNS is fine, the database is fine.
**Fix.** `helm rollback tracker` (or re-apply the correct values). Rollout completes.

## Fault 2: the Ingress sends /api to a Service that does not exist

`fault-2-ingress-wrong-service.yaml` edits the Ingress so `/api` points at `tracker-backend-v2`.

**Symptom.** The UI loads (its path is fine) but every API call fails; `curl /api/issues/stats`
through the Ingress returns `503 Service Temporarily Unavailable` from the controller.
**Investigation.** `kubectl describe ingress tracker` shows `/api -> tracker-backend-v2:80
(<error: services "tracker-backend-v2" not found>)`; `kubectl get svc` lists `tracker-backend`
with endpoints; `curl` to it from inside the cluster returns JSON, so the application is healthy
and only the routing is wrong.
**Root cause.** Ingress path points at a misspelled Service name.
**Fix.** `kubectl apply` the correct Ingress (or `helm upgrade` with the chart's template).

Both runs are captured in the project README. The lesson both share: when the status is
`Running` and the symptom is "wrong answer", the application is usually innocent and the
wiring (config, DNS names, routing) is where to look.
