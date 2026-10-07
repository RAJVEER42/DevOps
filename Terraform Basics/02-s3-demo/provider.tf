# AWS provider. With `use_localstack = true` every API call goes to a LocalStack container on
# localhost:4566 instead of AWS, with dummy credentials. Set it to false (the default) and
# configure real credentials with `aws configure` to run the same code against AWS.
provider "aws" {
  region = var.aws_region

  access_key = var.use_localstack ? "test" : null
  secret_key = var.use_localstack ? "test" : null

  skip_credentials_validation = var.use_localstack
  skip_metadata_api_check     = var.use_localstack
  skip_requesting_account_id  = var.use_localstack
  s3_use_path_style           = var.use_localstack

  dynamic "endpoints" {
    for_each = var.use_localstack ? [1] : []
    content {
      s3  = "http://localhost:4566"
      sts = "http://localhost:4566"
    }
  }
}
