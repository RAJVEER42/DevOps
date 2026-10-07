# Terraform and Infrastructure as Code

**Name:** Rajveer Bishnoi
**Enrollment Number:** 24BCS10404

| Folder | Contents |
|---|---|
| [01-iac-and-terraform/](01-iac-and-terraform/) | Why infrastructure as code, how Terraform works, the block types, providers, variables, the workflow, state, destroy |
| [02-s3-demo/](02-s3-demo/) | A complete Terraform project for an S3 bucket with the full `init` to `destroy` workflow run and captured |
| [03-aws-services/](03-aws-services/) | Notes on IAM, EC2, S3, VPC, and DynamoDB with RDS |

The demo was run against LocalStack so it needs no AWS account; a single variable switches it
to real AWS. Details in the demo README. The network project that builds on this is in
[Cloud Terraform](../Cloud%20Terraform/).

Tooling: Terraform v1.16, AWS provider v5.100, LocalStack 3.8, AWS CLI v2.
