# Infrastructure

The cloud side of this project is the Terraform work from sessions 18 and 19, kept in their
own folders so each can be run and destroyed independently:

| Project | Builds | Status |
|---|---|---|
| [Terraform Basics/02-s3-demo](../../Terraform%20Basics/02-s3-demo/) | An S3 bucket for artefacts and Terraform state, with versioning, encryption and public-access block | Applied and destroyed against LocalStack; one variable switches to AWS |
| [Cloud Terraform/02-vpc-project](../../Cloud%20Terraform/02-vpc-project/) | VPC, two public subnets across two AZs, internet gateway, route table, web security group, optional EC2 | Applied and destroyed against LocalStack; same switch |

## Where the cluster comes from

This project ran on **Minikube**. The homework's EKS module needs an AWS account and roughly
two to three dollars of spend per session (control plane, two `t3.medium` nodes, a NAT
gateway); it was not run because no account was available. The VPC project above is the
network an EKS cluster would be placed in; adding the cluster is one `module "eks"` block
from `terraform-aws-modules/eks/aws` pointed at those subnets, plus `aws eks update-kubeconfig`
and the same `helm upgrade --install` used here.

Everything the Kubernetes, Helm, CI/CD, monitoring and GitOps parts do is independent of which
cluster they target; that is the point of doing it on Minikube first.
