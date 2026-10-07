variable "aws_region" {
  type    = string
  default = "ap-south-1"
}

variable "project" {
  description = "Name prefix and Project tag"
  type        = string
  default     = "shop"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "vpc_cidr" {
  type    = string
  default = "10.20.0.0/16"
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "vpc_cidr must be a valid IPv4 CIDR block."
  }
}

variable "public_subnet_cidrs" {
  description = "One public subnet per entry, spread across availability zones"
  type        = list(string)
  default     = ["10.20.1.0/24", "10.20.2.0/24"]
}

variable "availability_zones" {
  type    = list(string)
  default = ["ap-south-1a", "ap-south-1b"]
}

variable "admin_cidr" {
  description = "Where SSH is allowed from. Never 0.0.0.0/0 in real life."
  type        = string
  default     = "203.0.113.10/32"
}

variable "create_instance" {
  description = "Also launch a t3.micro web server in the first public subnet"
  type        = bool
  default     = true
}

variable "use_localstack" {
  type    = bool
  default = false
}
