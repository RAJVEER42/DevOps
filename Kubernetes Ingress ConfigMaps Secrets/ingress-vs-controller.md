# Ingress vs Ingress Controller

## Ingress

An **Ingress** is a Kubernetes API object: a set of HTTP routing rules. It says "requests for
host `shop.local` with path `/api/` go to Service `catalog-api` on port 80". It can also name
a TLS Secret so HTTPS terminates at the edge. It is pure declaration. Creating one changes
nothing until something acts on it.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
spec:
  ingressClassName: nginx
  rules:
    - host: shop.local
      http:
        paths:
          - path: /api(/|$)(.*)
            backend: { service: { name: catalog-api, port: { number: 80 } } }
```

## Ingress Controller

An **Ingress Controller** is a program running in the cluster, usually a Deployment or
DaemonSet, that watches Ingress objects and configures a real reverse proxy to match. It is
not part of Kubernetes itself; you install one. ingress-nginx renders Ingress rules into an
nginx config and reloads nginx. Others: Traefik, HAProxy, Contour (Envoy), Istio's gateway,
and the cloud ones such as the AWS Load Balancer Controller that program an ALB instead of a
Pod-hosted proxy.

The controller also owns the entry point: a Service of type LoadBalancer or NodePort in front
of its own Pods. That single Service is what external traffic hits, no matter how many
Ingress objects and backend Services exist behind it.

## The difference in one table

| | Ingress | Ingress Controller |
|---|---|---|
| What it is | A resource (YAML) | Running software (Pods) |
| Who writes it | Application teams, per app | Platform team, once per cluster |
| Does anything by itself | No | Yes, but only what Ingress objects tell it |
| Scope | One host or path set | Every Ingress with its `ingressClassName` |
| Installed by default | The API type, yes | No. Minikube: `minikube addons enable ingress` |
| Analogy | A row in a routing table | The router |

## Why both are required

- Ingress without a controller: the object is stored, `kubectl get ingress` shows it, and no
  traffic moves. There is nothing listening. This is a common first-time surprise.
- Controller without Ingress objects: a proxy that returns 404 for everything, since it has
  no rules.

Kubernetes split them so the routing *rules* could be portable (the same Ingress YAML works
on Minikube with nginx and on EKS with an ALB) while the *implementation* can be swapped.
`ingressClassName` is the link: each controller claims a class and only acts on Ingresses
that name it. A cluster can run two controllers (say, internal and internet-facing) with
different classes.

## What the flow looks like

```
browser -> controller Service (NodePort / LoadBalancer)
        -> controller Pod (nginx)      reads Ingress rules, matches Host + path
        -> catalog-api Service (ClusterIP)
        -> one catalog-api Pod
```

In the demo in [03-ingress/](03-ingress/), the controller is `ingress-nginx-controller` in
the `ingress-nginx` namespace, the class is `nginx`, and the Ingress `shop` routes two paths
to two ClusterIP Services. The troubleshooting folder shows what happens when an Ingress
names a Service that does not exist: the controller logs the problem and answers 503, which
is the controller doing its job with a bad rule.

## Where this is heading

The Gateway API (`GatewayClass`, `Gateway`, `HTTPRoute`) is the successor to Ingress with the
same split, more expressive routing (header matching, traffic weights for canaries) and
clearer role separation. ingress-nginx, Traefik, Contour and Istio all implement it. Ingress
remains supported and is still what most clusters run today.
