# Kubernetes Workloads: Pods, ReplicaSets and Deployments

**Name:** Rajveer Bishnoi
**Enrollment Number:** 24BCS10404

Two parts. First, the four ways to roll a new version out with a Deployment, each run for
real with traffic flowing so the behaviour is visible. Second, the Pod lifecycle: twelve
small manifests that each put a Pod into one specific state, with the status and events that
state produces.

All runs are on Minikube (Kubernetes v1.37). The echo image `hashicorp/http-echo` is used for
the strategies because its response text can be set per version, so a `curl` loop through
the Service shows exactly which version answered each request.

## Part 1: Deployment strategies

| Folder | Strategy | Downtime | Resource cost | Rollback |
|---|---|---|---|---|
| [01-rolling-update](01-rolling-update/) | Replace Pods a few at a time | None | +1 Pod (`maxSurge`) | `kubectl rollout undo`, gradual |
| [02-blue-green](02-blue-green/) | Two full environments, flip the Service selector | None | 2x Pods | Flip the selector back, instant |
| [03-canary](03-canary/) | Old and new behind one Service, ratio set by replica counts | None | +N canary Pods | Scale canary to 0, instant |
| [04-recreate](04-recreate/) | Kill everything, then start the new version | Yes | None extra | Re-apply old manifest, with downtime again |

Each folder has the manifests, the commands, the captured output and a short explanation of
what the output shows.

### How the strategies relate

Rolling update and Recreate are the two values of `spec.strategy.type` on a Deployment.
Kubernetes implements them. Blue-green and canary are not Deployment features; they are
patterns built from two Deployments plus the way a Service selects Pods by label.

## Part 2: Pod lifecycle

[pod-lifecycle/](pod-lifecycle/) has one manifest per scenario and a README that walks through
each: Running, Pending, Succeeded, Failed, CrashLoopBackOff, ImagePullBackOff, readiness,
liveness and startup probes, init containers, a multi-container Pod, and graceful termination.

## Helper used throughout

A long-lived `client` Pod with `curl` so requests originate inside the cluster:

```bash
kubectl run client --image=curlimages/curl:8.10.1 --restart=Never --command -- sleep 7200
# then, e.g.
kubectl exec client -- sh -c 'for i in $(seq 1 10); do curl -s http://shop-web; done' | sort | uniq -c
```
