# Kubernetes Storage, HPA and Probes

**Name:** Rajveer Bishnoi
**Enrollment Number:** 24BCS10404

| Folder | What it covers |
|---|---|
| [01-volumes/](01-volumes/) | emptyDir, hostPath, PersistentVolume and PersistentVolumeClaim, StorageClass and dynamic provisioning, each run with a manifest |
| [02-hpa/](02-hpa/) | A CPU-bound app, a HorizontalPodAutoscaler, a load generator, and the scale-up and scale-down observed over eight minutes |
| [03-mini-project/](03-mini-project/) | Namespace, PVC, Deployment with startup, readiness and liveness probes, Service, HPA; persistence, routing and scaling verified |

Cluster: Minikube v1.39 (Kubernetes v1.37) with the `metrics-server` and `default-storageclass`
addons. Probes are also covered scenario by scenario in
[Kubernetes Workloads/pod-lifecycle](../Kubernetes%20Workloads/pod-lifecycle/) (07 to 09).

## The three ideas in one paragraph each

**Storage.** Containers lose their filesystem on restart. `emptyDir` gives a Pod scratch space
that dies with it; `hostPath` borrows a node directory; a PersistentVolumeClaim asks the
cluster for durable storage by size and access mode and a StorageClass provisions it on
demand. Pods reference the claim, never the disk.

**HPA.** The autoscaler reads CPU (or memory, or custom metrics) from metrics-server, compares
the average across Pods to a target expressed as a percentage of the container's request, and
sets the Deployment's replica count to `ceil(current x utilisation / target)` within the
min/max bounds. Scale-up is immediate; scale-down waits for a stabilisation window.

**Probes.** Startup probes protect slow starters; readiness probes decide whether a Pod gets
Service traffic; liveness probes restart a container that is up but not working. Each answers
a different question, which is why a production Deployment usually has all three.
