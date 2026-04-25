variable "project_name" {
  description = "Canonical project identifier used for naming and tagging AWS resources."
  type        = string
  default     = "adaptive-soc-ai-framework"

  validation {
    condition     = can(regex("^[a-z0-9-]{3,63}$", var.project_name))
    error_message = "project_name must be 3-63 characters of lowercase letters, numbers, and hyphens."
  }
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "production"

  validation {
    condition     = contains(["development", "staging", "production", "disaster-recovery"], var.environment)
    error_message = "environment must be one of: development, staging, production, disaster-recovery."
  }
}

variable "aws_region" {
  description = "Primary AWS region for workloads that may process regulated data."
  type        = string
  default     = "eu-central-1"

  validation {
    condition = contains([
      "eu-central-1",
      "eu-central-2",
      "eu-west-1",
      "eu-west-2",
      "eu-west-3",
      "eu-south-1",
      "eu-south-2",
      "eu-north-1",
      "eu-west-4",
    ], var.aws_region)
    error_message = "aws_region must be an EU region to support GDPR-oriented data residency defaults."
  }
}

variable "allowed_cidr_blocks" {
  description = "Trusted CIDR blocks allowed to reach administrative or exposed endpoints."
  type        = list(string)
  default     = []

  validation {
    condition     = alltrue([for cidr in var.allowed_cidr_blocks : can(cidrnetmask(cidr))])
    error_message = "Each value in allowed_cidr_blocks must be a valid IPv4 or IPv6 CIDR block."
  }
}

variable "vpc_cidr" {
  description = "Primary IPv4 CIDR block for the SOC foundation VPC."
  type        = string
  default     = "10.42.0.0/16"

  validation {
    condition     = can(cidrnetmask(var.vpc_cidr))
    error_message = "vpc_cidr must be a valid IPv4 CIDR block."
  }
}

variable "availability_zone_count" {
  description = "Number of availability zones to use for the regional foundation footprint."
  type        = number
  default     = 2

  validation {
    condition     = contains([2, 3], var.availability_zone_count)
    error_message = "availability_zone_count must be 2 or 3."
  }
}

variable "enable_encryption_at_rest" {
  description = "Enforce encryption at rest for supported services."
  type        = bool
  default     = true
}

variable "kms_key_deletion_window_in_days" {
  description = "KMS key deletion waiting period. Longer windows reduce accidental key loss risk."
  type        = number
  default     = 30

  validation {
    condition     = var.kms_key_deletion_window_in_days >= 7 && var.kms_key_deletion_window_in_days <= 30
    error_message = "kms_key_deletion_window_in_days must be between 7 and 30 days."
  }
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection on supported stateful services."
  type        = bool
  default     = true
}

variable "enable_access_logging" {
  description = "Enable audit and access logging on supported AWS services."
  type        = bool
  default     = true
}

variable "log_retention_in_days" {
  description = "Retention period for audit and security logs."
  type        = number
  default     = 365

  validation {
    condition = contains([
      30,
      60,
      90,
      120,
      180,
      365,
      400,
      545,
      731,
      1096,
      1827,
      2192,
      2557,
      2922,
      3288,
      3653,
    ], var.log_retention_in_days)
    error_message = "log_retention_in_days must match a supported CloudWatch Logs retention value."
  }
}

variable "data_classification" {
  description = "Data sensitivity classification used for tagging and downstream controls."
  type        = string
  default     = "confidential"

  validation {
    condition     = contains(["public", "internal", "confidential", "restricted"], var.data_classification)
    error_message = "data_classification must be one of: public, internal, confidential, restricted."
  }
}

variable "contains_personal_data" {
  description = "Whether the deployed workload processes personal data subject to GDPR controls."
  type        = bool
  default     = true
}

variable "resource_tags" {
  description = "Additional non-sensitive tags to merge into the standard governance tag set."
  type        = map(string)
  default = {
    ComplianceFramework = "GDPR"
    DataResidency       = "EU"
    ManagedBy           = "Terraform"
    SecurityBaseline    = "Gold"
  }

  validation {
    condition = alltrue([
      for key, value in var.resource_tags :
      length(trimspace(key)) > 0 &&
      length(trimspace(value)) > 0 &&
      !startswith(lower(key), "aws:")
    ])
    error_message = "resource_tags must use non-empty keys and values, and must not use the reserved aws: prefix."
  }
}
