# Security in the pipeline and the cluster

| Layer | Control | Where |
|---|---|---|
| Source | Tests must pass before any image is built | `issue-tracker-cicd.yml`, job 1 |
| Dependencies | Exact version pins in `requirements.txt`; pip-audit and Semgrep/bandit patterns from the DevSecOps session apply unchanged | `Issue Tracker Compose/backend/requirements.txt`, [DevSecOps Pipeline](../../DevSecOps%20Pipeline/) |
| Secrets | gitleaks over history in the DevSecOps workflow; no credentials in any committed file; the Helm chart's demo password is replaced by `postgres.existingSecret` in `values-prod.yaml` | `.gitleaks.toml`, `helm/issue-tracker/values-prod.yaml` |
| Images | Both images built in CI, scanned with Trivy for HIGH/CRITICAL with a fix available, the job fails on any finding, JSON reports kept as artifacts; only then pushed, tagged with the git SHA, never `latest` | `issue-tracker-cicd.yml`, job 2 |
| Image hygiene | Multi-stage builds, slim and alpine bases, fixed non-root UIDs, `HEALTHCHECK`, `.dockerignore` | `Issue Tracker Compose/*/Dockerfile` |
| Runtime | Backend runs `runAsNonRoot`, no privilege escalation, all capabilities dropped; resource limits on every container; startup, readiness and liveness probes | `helm/issue-tracker/templates/backend.yaml` |
| Network | Only the frontend and `/api` are exposed through the Ingress; postgres has no Ingress and no NodePort; nginx proxies to the backend Service by name | `templates/ingress.yaml`, `templates/frontend.yaml` |
| Registry | GHCR images are private; the cluster pulls with a short-lived token stored as an `imagePullSecret` | deploy job, `image.pullSecret` value |
| Supply chain | Actions pinned to major versions; provider versions pinned in Terraform with a committed lock file | workflows, `*.tf` |

## Trivy policy

```
severity: HIGH,CRITICAL
ignore-unfixed: true      # a CVE with no patch available is reported, not blocking
exit-code: 1              # anything else fails the job before the push step
```

The reasoning: a vulnerability we can fix by bumping a version should block the build; one with
no fix anywhere yet should be visible but should not freeze all releases.

## What to add for production

External Secrets Operator or Sealed Secrets for the database password, image signing with
cosign and an admission policy that rejects unsigned images, a NetworkPolicy restricting
postgres ingress to the backend Pods, and a read-only root filesystem on the backend (it
needs a writable `/tmp`, as the DevSecOps session found).
