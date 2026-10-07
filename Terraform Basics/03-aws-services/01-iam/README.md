# IAM, Identity and Access Management

## What it is

IAM is the AWS service that decides **who** can do **what** to **which** resource. Every API
call to AWS, whether from the console, the CLI, Terraform or an EC2 instance, is authenticated
as some principal and then authorised against IAM policies. There is no "inside the network"
exemption; IAM is the perimeter.

## The pieces

| Object | What it is | Typical use |
|---|---|---|
| **User** | A long-lived identity for a person or a legacy system, with a password and/or access keys | Individual engineers; increasingly replaced by SSO |
| **Group** | A set of users that share policies | `developers`, `billing-readers`. Attach policies to groups, not users |
| **Role** | An identity with no permanent credentials that something **assumes** to get temporary ones | EC2 instances, Lambda functions, EKS Pods, cross-account access, CI runners |
| **Policy** | A JSON document listing allowed or denied actions on resources, with optional conditions | Attached to users, groups or roles (identity policies) or to resources like S3 buckets (resource policies) |
| **Permission** | One `Action` on one `Resource` with an `Effect` | `s3:GetObject` on `arn:aws:s3:::my-bucket/*` |

A policy statement:

```json
{
  "Effect": "Allow",
  "Action": ["s3:GetObject", "s3:ListBucket"],
  "Resource": ["arn:aws:s3:::devops-course-artifacts-*", "arn:aws:s3:::devops-course-artifacts-*/*"],
  "Condition": {"Bool": {"aws:SecureTransport": "true"}}
}
```

Evaluation: everything is denied by default; an explicit `Allow` grants; an explicit `Deny`
anywhere wins over any allow.

## Roles are the important one

Roles solve the credential problem. An EC2 instance with an **instance profile** gets
short-lived keys from the metadata service, rotated automatically, scoped to that role. An EKS
Pod with IAM Roles for Service Accounts gets the same. A GitHub Actions job can assume a role
via OIDC with no stored secret at all. In each case nothing long-lived exists to leak.

## Least privilege

Grant exactly the actions on exactly the resources a task needs, and nothing more. In practice:
start from a managed policy, watch IAM Access Analyzer or CloudTrail for what is actually used,
then narrow. The `02-s3-demo` Terraform run needs `s3:*` on one bucket prefix and nothing else;
`AdministratorAccess` would work but is the wrong answer.

## Best practices

- Enable MFA on the root account and never use the root account for daily work.
- Humans sign in through IAM Identity Center (SSO); no long-lived access keys for people.
- Workloads use roles, never embedded keys. Rotate any key that must exist.
- Attach policies to groups and roles, not to individual users.
- Use conditions: source IP, MFA present, `aws:SecureTransport`, resource tags.
- Turn on CloudTrail so every API call is logged, and Access Analyzer to spot over-broad access.
- Use permission boundaries and service control policies (Organizations) to cap what even an
  admin in a sub-account can grant.

## Common use cases

- A CI pipeline assumes a deploy role that can push to ECR and update one ECS service.
- A web server's instance role can read one S3 bucket and write to one CloudWatch log group.
- A read-only group for auditors with `ReadOnlyAccess`.
- Cross-account access: a role in the production account trusts the CI account.
- A bucket policy that lets a partner account read specific objects.
