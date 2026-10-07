# Helm

**Name:** Rajveer Bishnoi
**Enrollment Number:** 24BCS10404

Helm packages a set of Kubernetes manifests into a **chart**, fills in the variable parts
from a `values.yaml`, and tracks each installed copy as a **release** with a numbered
revision history. That history is what makes `helm rollback` a one-liner.

| Folder | Contents |
|---|---|
| [01-commands/](01-commands/) | Every day-to-day Helm command run against a scaffolded chart, with output |
| [02-rollback/](02-rollback/) | A small chart and the full install, upgrade, upgrade, rollback cycle |
| [03-mini-project/](03-mini-project/) | `notes-chart`: a chart with dev and prod value files, installed both ways |

Helm v4.3 on Minikube (Kubernetes v1.37). Install on macOS with `brew install helm`.

## Vocabulary

| Term | Meaning |
|---|---|
| Chart | A directory with `Chart.yaml`, `values.yaml` and `templates/` |
| Values | The inputs to the templates. Defaults in `values.yaml`, overridden by `-f file` or `--set key=value` |
| Release | One installed instance of a chart under a name. The same chart can be released many times |
| Revision | Each install, upgrade or rollback of a release increments it. Stored as a Secret in the namespace |
| Repository | An HTTP index of packaged charts (`helm repo add`), searched with `helm search repo` |

## The commands in one place

```bash
helm create NAME                 # scaffold a chart
helm lint CHART                  # check it
helm template REL CHART          # render locally, no cluster
helm install REL CHART [-f values.yaml] [--set k=v] [--wait]
helm list                        # releases in the namespace
helm status REL                  # state, revision, notes
helm get values|manifest|notes REL
helm upgrade REL CHART ...       # new revision
helm history REL                 # all revisions
helm rollback REL [REVISION]     # new revision that restores an old one
helm uninstall REL
helm repo add|update|list
helm search repo|hub TERM
```
