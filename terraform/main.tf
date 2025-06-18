# FOCUS Generator Infrastructure as Code
# This Terraform configuration creates the AWS infrastructure for the FOCUS Generator

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Backend configuration for state management
  backend "s3" {
    # These values should be configured during initialization
    # bucket = "your-terraform-state-bucket"
    # key    = "focus-generator/terraform.tfstate"
    # region = "us-east-1"
    # dynamodb_table = "terraform-locks"
    # encrypt = true
  }
}

# Provider configuration
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "FOCUS-Generator"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Repository  = "https://github.com/wjesseclements/FOCUS-generator"
    }
  }
}

# Local values for common configurations
locals {
  name_prefix = "focus-generator-${var.environment}"
  
  common_tags = {
    Project     = "FOCUS-Generator"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}