variable "aws_region" {
  description = "Region to create the bucket in"
  type        = string
  default     = "ap-south-1"
}

variable "bucket_prefix" {
  description = "Bucket names are global, so a random suffix is appended to this prefix"
  type        = string
  default     = "devops-course-artifacts"

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9-]{2,40}$", var.bucket_prefix))
    error_message = "Lowercase letters, digits and hyphens only, 3 to 41 characters."
  }
}

variable "environment" {
  description = "Tag applied to everything"
  type        = string
  default     = "dev"
}

variable "enable_versioning" {
  description = "Keep previous versions of overwritten or deleted objects"
  type        = bool
  default     = true
}

variable "use_localstack" {
  description = "Point the provider at a local LocalStack container instead of AWS"
  type        = bool
  default     = false
}
