# Kubernetes object comparison

Three pairings that come up constantly, explained from the point of view of "which one do I
reach for and why".

## Deployment vs ReplicaSet

| | ReplicaSet | Deployment |
|---|---|---|
| Purpose | Keep exactly N copies of a Pod template running | Manage ReplicaSets over time so you can change the template safely |
| Pod management | Creates or deletes Pods to match `replicas`; selects them by label | Does not touch Pods directly; owns ReplicaSets and sets their replica counts |
| Scaling | `kubectl scale rs/x --replicas=N` works, but is undone if a Deployment owns it | `kubectl scale deploy/x` or edit `spec.replicas`; also the target for HPA |
| Rolling updates | None. Changing the template does nothing to existing Pods | Yes. A new template creates a new ReplicaSet and shifts replicas across per `strategy` |
| Rollback | Not a concept | `kubectl rollout undo`, revision history kept per `revisionHistoryLimit` |

**Relationship.** A Deployment is a controller for ReplicaSets, and a ReplicaSet is a
controller for Pods. Every time the Pod template changes, the Deployment creates a ReplicaSet
with a new pod-template hash in its name (the `shop-web-7fdcd98999` style suffix), scales it
up and scales the old one down. Old ReplicaSets are kept at zero replicas so a rollback is just
"scale that one back up". You can see the chain with:

```bash
kubectl get deploy,rs,pods -l app=shop-web
kubectl get rs shop-web-864476887c -o jsonpath='{.metadata.ownerReferences[0].kind}'   # Deployment
kubectl get pod shop-web-864476887c-f6bsw -o jsonpath='{.metadata.ownerReferences[0].kind}'   # ReplicaSet
```

In practice you almost never write a ReplicaSet by hand. You write a Deployment and let it
create them. The same Pod spec, wrapped in a Deployment, gains updates and rollbacks for free.

## Deployment vs DaemonSet vs StatefulSet

All three run Pods from a template; they differ in *how many*, *where* and *with what identity*.

| | Deployment | DaemonSet | StatefulSet |
|---|---|---|---|
| Use case | Stateless services: web servers, APIs, workers | One agent per node: log shippers, node monitoring, CNI, storage drivers | Stateful, ordered systems: databases, message brokers, anything with a stable identity |
| Pod creation | `replicas` interchangeable Pods with random suffixes, scheduled anywhere | Exactly one Pod on every node that matches the node selector or tolerations. Adding a node adds a Pod | Ordinal Pods `name-0`, `name-1`, ... created in order, each waiting for the previous to be Ready |
| Scaling | Set `replicas`; HPA can drive it | No replica count. Scales with the node count | Set `replicas`; scales up in order and down in reverse order |
| Networking | Reach through a Service; no per-Pod identity | Usually reached via `hostPort`, `hostNetwork` or node-local addressing | Headless Service gives each Pod a stable DNS name: `name-0.svc.ns.svc.cluster.local` |
| Storage | Shared or none; a PVC in the template is shared by all replicas | Typically `hostPath` to read node files | `volumeClaimTemplates` give each Pod its own PVC that survives rescheduling |
| Updates | RollingUpdate or Recreate | RollingUpdate node by node, or OnDelete | RollingUpdate in reverse ordinal order, with optional partition for canaries |
| Example | `nginx`, a REST API, the `shop-web` echo service | Fluent Bit, node-exporter, kube-proxy itself | PostgreSQL, Kafka, ZooKeeper, Elasticsearch |

A rule of thumb: if two Pods could swap places and nothing would notice, use a Deployment.
If a Pod belongs to a node, use a DaemonSet. If a Pod has a name that matters or data that
is its own, use a StatefulSet.

## ReplicaSet vs Service

These are often confused because both have a label selector. They answer different questions.

| | ReplicaSet | Service |
|---|---|---|
| Responsibility | **How many** Pods exist. Creates and deletes them | **How to reach** Pods. A stable IP and DNS name in front of whichever Pods match |
| Reacts to | Pod count drifting from `replicas` | Pods appearing, disappearing or changing readiness |
| Owns Pods | Yes (ownerReferences) | No. It only lists them in an EndpointSlice |
| Without it | Pods are not replaced when they die | Pods exist but have changing IPs and nothing load-balances across them |

**Why a Service is required.** Pod IPs are ephemeral. Every time a ReplicaSet replaces a Pod
the new one gets a new IP. A client cannot hard-code `10.244.0.37`. The Service gives one
ClusterIP and one DNS name that stay constant for the life of the Service, regardless of how
many Pods are behind it or how often they change.

**How traffic reaches Pods.**

1. The client resolves `web-clusterip.default.svc.cluster.local` via CoreDNS and gets the
   ClusterIP (`10.109.223.166` in the Services run).
2. The EndpointSlice controller keeps a list of ready Pod IPs that match the Service selector.
3. kube-proxy on every node programs iptables (or IPVS) rules: traffic to `ClusterIP:port` is
   DNAT'd to one of those Pod IPs on `targetPort`.
4. The packet reaches the Pod. The Pod does not know a Service was involved.

The ReplicaSet keeps step 2's list populated; the Service makes the list usable. Together
they are what "deploy an app" means in Kubernetes, which is why `kubectl create deployment`
plus `kubectl expose` is the first thing every tutorial does.
