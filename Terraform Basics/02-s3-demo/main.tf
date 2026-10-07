# One private S3 bucket with a random suffix, versioning, encryption, a public-access block,
# a lifecycle rule and one object uploaded into it.

resource "random_id" "suffix" {
  byte_length = 3
}

locals {
  bucket_name = "${var.bucket_prefix}-${random_id.suffix.hex}"
  tags = {
    Project     = "devops-course"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket" "artifacts" {
  bucket = local.bucket_name
  tags   = local.tags
}

resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Suspended"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "artifacts" {
  bucket                  = aws_s3_bucket.artifacts.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "artifacts" {
  # LocalStack's community edition never reports the rule as applied, so skip it there.
  count  = var.use_localstack ? 0 : 1
  bucket = aws_s3_bucket.artifacts.id
  rule {
    id     = "expire-old-build-logs"
    status = "Enabled"
    filter {
      prefix = "build-logs/"
    }
    expiration {
      days = 30
    }
  }
}

resource "aws_s3_object" "readme" {
  bucket       = aws_s3_bucket.artifacts.id
  key          = "README.txt"
  content      = "Created by Terraform for the DevOps course. Environment: ${var.environment}\n"
  content_type = "text/plain"
  tags         = local.tags
}
