terraform {
  # Pinned to the current stable Terraform 1.14 patch line.
  required_version = "~> 1.14.8"

  required_providers {
    aws = {
      source = "hashicorp/aws"
      # Pinned to the latest verified 6.x release line from the Terraform Registry.
      version = "~> 6.39.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  # Global governance tags: keep values non-sensitive and GDPR-oriented.
  default_tags {
    tags = merge(var.resource_tags, {
      Project              = var.project_name
      Environment          = var.environment
      ComplianceFramework  = "GDPR"
      ContainsPersonalData = tostring(var.contains_personal_data)
      DataClassification   = var.data_classification
    })
  }
}
