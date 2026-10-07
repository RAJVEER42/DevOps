# Kubernetes Troubleshooting

**Name:** Rajveer Bishnoi
**Enrollment Number:** 24BCS10404

"The app is not working." This folder is about turning that sentence into a root cause with
a fixed set of commands and a fixed order of questions. Everything was run on Minikube; each
scenario has a deliberately broken manifest, the commands that found the problem, the fixed
manifest, and the before and after output.

| Folder | Contents |
|---|---|
| [01-commands/](01-commands/) | `get`, `describe`, `logs`, `exec`, `events`, `explain`, `top`, `-o wide`, plus `port-forward` and `debug`, each run against a healthy demo app |
| [02-scenarios/](02-scenarios/) | Nine broken manifests: CrashLoopBackOff, ImagePullBackOff, ErrImagePull (private registry), Pending, ContainerCreating, Service connectivity, DNS, Pod networking, configuration |
| [03-mini-project/](03-mini-project/) | A Deployment, Service and Pod "deployed by the team" with two planted faults, diagnosed and fixed |

## The order of questions

```
1. What state is it in?          kubectl get pods -o wide            (STATUS, READY, RESTARTS, node, IP)
2. Why is it in that state?      kubectl describe pod X              (read the Events at the bottom)
3. What did the process say?     kubectl logs X [--previous]         (for anything that started and died)
4. Is it the Pod or the path?    kubectl get endpointslices, describe svc, exec curl   (for "cannot reach")
5. Is it the cluster?            kubectl get nodes, top nodes, events --types=Warning -A
```

Most problems are answered at step 2. The status column alone narrows it a lot:

| STATUS | Usually means | First command |
|---|---|---|
| `Pending`, no node | Scheduler cannot place it: resources, selectors, taints, missing PVC | `describe pod` -> `FailedScheduling` |
| `ContainerCreating` for long | Volume or image pull in progress or failing | `describe pod` -> `FailedMount` or `Pulling` |
| `ImagePullBackOff`, `ErrImagePull` | Wrong image name/tag, or no credentials | `describe pod` -> `Failed to pull`, read the registry's message |
| `CreateContainerConfigError` | Missing ConfigMap/Secret key referenced in env | `describe pod` -> `couldn't find key` |
| `CrashLoopBackOff`, `Error` | The process exits | `logs --previous` |
| `Running` but `0/1 READY` | Readiness probe failing | `describe pod` -> `Unhealthy`; the Pod is withheld from Services |
| `Running 1/1` but unreachable | Service selector, port or DNS | `get endpointslices`, `describe svc`, `dig` from a client Pod |
