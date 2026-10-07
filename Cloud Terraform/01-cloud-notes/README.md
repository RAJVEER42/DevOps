# Cloud fundamentals, as much as the project needs

## Service models

| Model | You manage | Provider manages | AWS examples |
|---|---|---|---|
| IaaS | OS, runtime, app, scaling, patching | Hardware, network, virtualisation | EC2, EBS, VPC |
| PaaS | Your code and configuration | Everything underneath, including the runtime | Elastic Beanstalk, RDS, EKS control plane |
| SaaS | Your data and settings | The whole application | Amazon WorkMail, GitHub, Datadog |

Terraform mostly provisions IaaS and PaaS pieces. The VPC project here is pure IaaS: a network
and, optionally, a virtual machine, with everything above the OS left to us.

## Regions and availability zones

A **region** (`ap-south-1`, Mumbai) is a geographic area with its own set of services and
pricing; data stays in a region unless you move it. Inside a region are two or more
**availability zones** (`ap-south-1a`, `1b`, `1c`): physically separate data centres with
independent power and networking, joined by low-latency links. A subnet lives in exactly one
AZ; an application survives an AZ outage only if it is spread across at least two. That is why
the project creates two public subnets in two AZs rather than one.

## VPC, subnets, routing, gateways, security groups

Covered in depth in [Terraform Basics/03-aws-services/04-vpc](../../Terraform%20Basics/03-aws-services/04-vpc/).
The short version, in the order the project creates them:

1. **VPC** `10.20.0.0/16`: the private address space.
2. **Subnets** `10.20.1.0/24` in `1a`, `10.20.2.0/24` in `1b`: slices of it, one per AZ, with
   `map_public_ip_on_launch` so instances get a public IP.
3. **Internet Gateway**: the VPC's door to the internet.
4. **Route table** with `0.0.0.0/0 -> igw` and an **association** to each subnet: the thing that
   actually makes those subnets public. The `local` route for the VPC CIDR is implicit.
5. **Security group**: 80 and 443 from anywhere, 22 only from one admin `/32`, all outbound.
6. **EC2 instance** (optional): `t3.micro` on the latest Amazon Linux 2023 looked up with a
   `data "aws_ami"` block, in the first public subnet, with user data that installs nginx.

## Terraform concepts this project exercises

| Concept | Where |
|---|---|
| Provider configuration with a switch | `versions.tf`, the `dynamic "endpoints"` block |
| Variables with types, defaults and validation | `variables.tf`, `vpc_cidr` validation |
| Lists and `count` | one `aws_subnet` resource producing two subnets, indexed into two AZs |
| Implicit dependencies | `aws_subnet.public[*].vpc_id = aws_vpc.main.id` and so on; `terraform graph` shows the result |
| Data sources | `data "aws_ami" "al2023"` reads instead of creates |
| Conditional resources | `count = var.create_instance ? 1 : 0` |
| `locals` and `merge()` for tags | every resource gets `Project`, `Environment`, `ManagedBy`, plus a `Name` |
| Outputs including splat expressions | `aws_subnet.public[*].id` |
| State | `terraform state list` before and after destroy |
| `plan` / `apply` / `destroy` | all captured in `02-vpc-project` |
