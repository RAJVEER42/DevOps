# Infrastructure as Code and Terraform

## Why infrastructure as code

Clicking through a cloud console works once. The second environment is slightly different,
nobody remembers why, and three months later nobody can rebuild it. Infrastructure as Code
puts the infrastructure in text files, so it gets what application code already has: version
control, review, diffs, repeatability, and a way to destroy and recreate on demand.

Two flavours exist. **Imperative** tools (shell scripts, Ansible playbooks) list steps to run.
**Declarative** tools (Terraform, CloudFormation, Pulumi) describe the end state and work out
the steps themselves. Terraform is declarative: you write "one bucket with versioning", not
"call CreateBucket, then PutBucketVersioning".

## How Terraform works

```
 .tf files  ──>  terraform plan  ──>  execution plan  ──>  terraform apply  ──>  cloud API calls
     ▲                   │                                        │
     │             reads state                             writes state
     └──── you edit ─────┴──────────── terraform.tfstate ─────────┘
```

Terraform core reads the configuration, reads the **state file** (what it created last time),
asks the **provider** what currently exists, and computes the difference. The plan shows that
difference; apply executes it and updates the state. Resources are built as a dependency graph,
so independent ones are created in parallel and dependent ones wait.

## The building blocks

| Block | Purpose | Example in `02-s3-demo` |
|---|---|---|
| `terraform {}` | Required Terraform and provider versions | `required_providers { aws = { version = "~> 5.80" } }` |
| `provider "aws" {}` | How to talk to one API: region, credentials, endpoints | region from a variable, optional LocalStack endpoints |
| `resource "TYPE" "NAME" {}` | One thing to create and manage | `aws_s3_bucket.artifacts`, `aws_s3_bucket_versioning.artifacts` |
| `variable "x" {}` | An input with a type, default and validation | `bucket_prefix` with a regex validation |
| `locals {}` | Computed values used in several places | `bucket_name`, the shared `tags` map |
| `output "x" {}` | Values to print after apply and to pass to other configs | `bucket_name`, `bucket_arn` |
| `data "TYPE" "NAME" {}` | Read something that already exists instead of creating it | `data "aws_ami"` for the latest Amazon Linux |
| `module "x" {}` | A reusable folder of the above | `terraform-aws-modules/vpc/aws` |

References like `aws_s3_bucket.artifacts.id` are how one resource depends on another;
Terraform infers the graph from them.

## Providers

A provider is a plugin that maps resource types to one API: `hashicorp/aws`, `hashicorp/google`,
`hashicorp/kubernetes`, `hashicorp/random`. `terraform init` downloads the versions allowed by
`required_providers` and records the exact ones in `.terraform.lock.hcl`, which is committed so
every machine uses the same plugin builds.

## Variables and values

Precedence, lowest to highest: the `default` in the variable block, `terraform.tfvars`,
`*.auto.tfvars`, `TF_VAR_name` environment variables, and `-var` / `-var-file` on the command
line. `terraform.tfvars` is for non-secret settings; credentials never go in any of these files.
They come from the environment or the AWS CLI profile.

## The workflow

```bash
terraform init       # download providers, set up the backend
terraform fmt        # canonical formatting
terraform validate   # syntax and type checks, no API calls
terraform plan       # what would change
terraform apply      # make it so (asks for confirmation unless -auto-approve)
terraform show       # the current state, human readable
terraform output     # just the outputs
terraform destroy    # remove everything in the state
```

`plan -out=tfplan` followed by `apply tfplan` guarantees apply does exactly what was reviewed.

## State

`terraform.tfstate` maps each resource address in the config to the real object's id and
attributes. It is how Terraform knows that `aws_s3_bucket.artifacts` **is**
`devops-course-artifacts-c7d363` and should be updated rather than created again. Rules:

- Never edit it by hand; use `terraform state mv|rm|import`.
- Never commit it; it can contain secrets and it goes stale. It is in `.gitignore`.
- For a team, store it remotely (an S3 bucket with DynamoDB locking, or Terraform Cloud) so
  two people cannot apply at once.

## Destroy

`terraform destroy` walks the graph in reverse and deletes everything in the state. It is the
reason IaC environments are cheap: a lab that costs money per hour exists only while you need
it. The S3 demo ends with a destroy and an empty `terraform state list`.

## This folder

- [02-s3-demo/](../02-s3-demo/): the complete workflow on a real resource set, run against
  LocalStack with the output captured.
- [03-aws-services/](../03-aws-services/): notes on IAM, EC2, S3, VPC, DynamoDB and RDS.
