output "bucket_name" {
  description = "The generated bucket name"
  value       = aws_s3_bucket.artifacts.bucket
}

output "bucket_arn" {
  value = aws_s3_bucket.artifacts.arn
}

output "bucket_region" {
  value = aws_s3_bucket.artifacts.region
}

output "versioning" {
  value = aws_s3_bucket_versioning.artifacts.versioning_configuration[0].status
}

output "readme_object_key" {
  value = aws_s3_object.readme.key
}
