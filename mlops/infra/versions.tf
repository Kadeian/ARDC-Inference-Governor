terraform {
  required_version = ">= 1.10, < 2.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
  # Configure an encrypted, versioned S3 backend with use_lockfile=true at init.
  # Never use local state for shared or production environments.
}
provider "aws" {
  region = var.region
  default_tags {
    tags = { Project = "clarity4life-mlops", Environment = var.environment }
  }
}
