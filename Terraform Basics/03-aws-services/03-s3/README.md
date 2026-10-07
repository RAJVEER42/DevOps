# S3, Simple Storage Service

## What it is

Object storage: you put a blob of bytes under a key in a bucket and get it back by that key over
HTTPS. No filesystem, no block device, no limit on total size, eleven nines of durability
because every object is stored redundantly across at least three availability zones. It is the
default place in AWS for anything that is a file: build artefacts, logs, backups, static
websites, data lakes, Terraform state.

## Buckets and objects

A **bucket** is a namespace with a globally unique name (across all AWS accounts, which is why
the Terraform demo appends a random suffix) living in one region. It holds **objects**: a key
(the full "path", slashes are just characters), the data (up to 5 TB), metadata, and a
version id if versioning is on. There are no real directories; the console fakes them from
prefixes.

```
s3://devops-course-artifacts-c7d363/build-logs/2026-10-07/ci-1234.log
       bucket                        key
```

## Storage classes

| Class | For | Trade-off |
|---|---|---|
| Standard | Frequently read data | Highest per-GB price, no retrieval fee |
| Intelligent-Tiering | Unknown or changing access patterns | Moves objects between tiers automatically for a small monitoring fee |
| Standard-IA / One Zone-IA | Read rarely, needed instantly | Cheaper storage, per-GB retrieval fee, 30-day minimum |
| Glacier Instant / Flexible / Deep Archive | Archives, compliance | Cheapest storage; minutes to hours to retrieve; 90 to 180-day minimum |

## Versioning

With versioning on, overwriting or deleting an object keeps the previous version; a delete
just adds a "delete marker". It protects against accidental overwrites and ransomware-style
deletion, at the cost of storing every version until a lifecycle rule expires them. The demo
bucket has it enabled and the run shows `terraform apply -var enable_versioning=false`
suspending it.

## Lifecycle policies

Rules that act on objects by age or prefix: transition to a cheaper class after N days,
expire after M days, clean up old versions and incomplete multipart uploads. The demo defines
one rule expiring `build-logs/` after 30 days. Lifecycle is how an S3 bill stays flat while the
data keeps arriving.

## Encryption

Everything in S3 is encrypted at rest by default since 2023 with SSE-S3 (AES-256, AWS-managed
keys). SSE-KMS uses a key you control in KMS, with its own audit trail and the ability to
revoke access by disabling the key. Client-side encryption is possible for data that must never
be readable by AWS. In transit, enforce HTTPS with a bucket policy condition on
`aws:SecureTransport`. The demo sets SSE-S3 explicitly.

## Access control

- **Block Public Access** at the account and bucket level is on by default and should stay on
  unless a bucket is genuinely a public website. The demo turns all four settings on.
- **Bucket policies** are resource-based IAM policies: who may do what to this bucket. Used for
  cross-account access, enforcing TLS, or allowing a CloudFront distribution to read.
- **IAM policies** on the caller's identity are the other half; a request needs to be allowed
  by one and not denied by either.
- ACLs are legacy and disabled by default on new buckets.
- Pre-signed URLs grant time-limited access to one object without any IAM identity.

## Common use cases

- Terraform remote state, with DynamoDB for locking.
- CI artefacts, container image layers (ECR is built on S3), Helm chart repositories.
- Log archive from CloudTrail, ALB, VPC Flow Logs.
- Static website or SPA hosting behind CloudFront.
- Data lake queried in place by Athena.
- Backups and database snapshot exports.
