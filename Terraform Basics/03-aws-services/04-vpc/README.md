# VPC, Virtual Private Cloud

## What it is

Your own isolated network inside AWS: a private IP range that you carve into subnets and wire
to the internet, to other VPCs, or to your office exactly as you choose. Every EC2 instance,
RDS database, EKS node and load balancer lives in a VPC subnet. Nothing in it is reachable from
outside unless you add a route and allow it through a firewall.

## CIDR

The VPC's address range in CIDR notation: `10.20.0.0/16` is 65,536 addresses from 10.20.0.0 to
10.20.255.255. Subnets take slices of it: `10.20.1.0/24` is 256 addresses (AWS reserves five
per subnet). Pick ranges that do not overlap with other VPCs or the office network, or peering
and VPNs become impossible later. RFC 1918 ranges (`10/8`, `172.16/12`, `192.168/16`) are the
convention.

## Subnets

A subnet is a CIDR slice pinned to **one availability zone**. Spreading subnets across two or
three AZs is what makes an application survive a data-centre failure. A subnet is "public" or
"private" purely by its route table:

```
VPC 10.20.0.0/16
├── public-a   10.20.1.0/24   (ap-south-1a)  route 0.0.0.0/0 -> Internet Gateway
├── public-b   10.20.2.0/24   (ap-south-1b)  route 0.0.0.0/0 -> Internet Gateway
├── private-a  10.20.11.0/24  (ap-south-1a)  route 0.0.0.0/0 -> NAT Gateway
└── private-b  10.20.12.0/24  (ap-south-1b)  route 0.0.0.0/0 -> NAT Gateway
```

## Route tables

Each subnet is associated with one route table; a table can serve many subnets. Every table has
a `local` route for the VPC CIDR that cannot be removed. Adding `0.0.0.0/0 -> igw-...` makes a
subnet public. Adding `0.0.0.0/0 -> nat-...` makes it private with outbound internet. No default
route means no internet at all.

## Internet Gateway

A horizontally scaled, redundant VPC attachment that does 1:1 NAT between an instance's public
IP and its private IP. One per VPC. An instance needs three things to be reachable from the
internet: a public or Elastic IP, a route to the IGW, and a security group that allows the port.

## NAT Gateway

Lets instances in private subnets start outbound connections (package updates, calling APIs)
while refusing inbound ones. Managed, placed in a public subnet, with an Elastic IP. It costs
per hour and per GB, which is why dev environments often use one NAT for all AZs and production
uses one per AZ for resilience.

## Security Groups

Stateful firewalls on network interfaces. Allow rules only; return traffic is automatically
allowed. Rules can reference other security groups, so "the database allows 5432 from the
app servers' group" works without knowing any IPs. The default group allows all traffic from
itself and nothing else inbound.

## Network ACLs

Stateless firewalls on **subnets**. Numbered allow and deny rules evaluated in order, in both
directions, and because they are stateless you must allow ephemeral return ports explicitly.
The default NACL allows everything. They are a coarse second layer: block a known-bad CIDR at
the subnet, leave fine-grained rules to security groups.

| | Security group | Network ACL |
|---|---|---|
| Attached to | Instance (ENI) | Subnet |
| Stateful | Yes | No |
| Rule types | Allow only | Allow and deny |
| Evaluation | All rules | In number order, first match |

## Public vs private subnet

| | Public | Private |
|---|---|---|
| Default route | Internet Gateway | NAT Gateway, or none |
| Instances have public IPs | Usually | Never |
| Reachable from the internet | If the security group allows | No |
| Typical tenants | Load balancers, bastions, NAT gateways | Application servers, databases, EKS nodes |

The pattern almost every architecture follows: load balancer in public subnets, everything
else in private subnets, databases in private subnets with a security group that only trusts
the application tier. The Terraform project in `../../Cloud Terraform/` builds the public half
of this and explains each resource.
