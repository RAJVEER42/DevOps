# EC2, Elastic Compute Cloud

## What it is

Virtual machines, rented by the second. An EC2 **instance** is a VM with a chosen CPU and
memory shape, a disk, a network interface in your VPC, and an operating system image. It is
the oldest and most general AWS compute service; containers (ECS, EKS) and serverless (Lambda)
are alternatives, but EC2 is what most of them run on underneath.

## The pieces

**AMI, Amazon Machine Image.** The template an instance boots from: OS plus any pre-installed
software. AWS publishes Amazon Linux, Ubuntu and Windows AMIs; you can bake your own with
Packer and launch a fleet from it. An AMI is region-specific.

**Instance types.** A family letter and a size: `t3.micro` (burstable, cheap, free tier),
`m6i.large` (general purpose), `c7g.xlarge` (compute optimised, Graviton ARM), `r6i` (memory),
`p4d` (GPU). Pick the family for the workload shape and the size for the capacity. Purchase
options: on-demand, reserved or savings plans for steady load, spot for interruptible work at
up to 90% off.

**Key pairs.** An SSH key pair whose public half is placed in the instance at launch. AWS never
stores the private half; lose it and you cannot log in. Session Manager (SSM) is the modern
alternative that needs no open port 22 and no key.

**Security groups.** A stateful firewall attached to the instance's network interface. Rules
allow traffic by protocol, port and source (a CIDR or another security group). Nothing is
allowed inbound by default; all outbound is allowed. "Allow 443 from 0.0.0.0/0 and 22 from the
office IP" is the usual web server group. Security groups are per-instance; network ACLs (see
VPC) are per-subnet.

**EBS, Elastic Block Store.** The instance's disks. Network-attached volumes that persist
independently of the instance (unless marked delete-on-termination), can be snapshotted, and
come in types: `gp3` general purpose SSD (the default), `io2` for high IOPS, `st1` throughput HDD.
Instance store is the other option: local NVMe that is fast and vanishes when the instance stops.

**Public vs private IP.** Every instance gets a private IP from its subnet; it keeps it for its
life. A public IP is optional, assigned from Amazon's pool at launch and **changes on stop/start**.
An Elastic IP is a public IP you own and can move between instances. Instances in a private
subnet have no public IP and reach the internet through a NAT gateway.

## Instance lifecycle

```
pending -> running -> stopping -> stopped -> (start) -> pending -> running
                   -> shutting-down -> terminated
```

- **Stop**: EBS-backed only; you stop paying for compute, keep paying for the volume; the public
  IP is released; the private IP stays.
- **Reboot**: OS restart, same host, same IPs.
- **Terminate**: gone, volumes deleted unless configured otherwise. Enable termination
  protection on anything that matters.
- **Hibernate**: RAM saved to EBS, resume where you left off.

User data is a script that runs on first boot, used to install packages or join a cluster.
Instance metadata at `169.254.169.254` tells the instance about itself and hands out the
role's temporary credentials.

## Common use cases

- Web and API servers behind an Application Load Balancer in an Auto Scaling group.
- Self-hosted CI runners, build agents, bastion hosts.
- Databases you manage yourself when RDS does not fit.
- Kubernetes worker nodes (EKS node groups are EC2 instances).
- Batch and GPU jobs on spot instances.
