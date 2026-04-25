output "name_prefix" {
  description = "Canonical name prefix derived from project and environment."
  value       = local.name_prefix
}

output "aws_region" {
  description = "AWS region selected for this deployment."
  value       = var.aws_region
}

output "availability_zones" {
  description = "Availability zones used for the foundation footprint."
  value       = local.selected_azs
}

output "vpc_id" {
  description = "Identifier of the foundation VPC."
  value       = aws_vpc.core.id
}

output "vpc_cidr" {
  description = "IPv4 CIDR block assigned to the foundation VPC."
  value       = aws_vpc.core.cidr_block
}

output "internet_gateway_id" {
  description = "Identifier of the internet gateway attached to the VPC."
  value       = aws_internet_gateway.core.id
}

output "nat_gateway_id" {
  description = "Identifier of the NAT gateway serving private subnets."
  value       = aws_nat_gateway.core.id
}

output "public_subnet_ids" {
  description = "Identifiers of the public subnets keyed by availability zone."
  value = {
    for az, subnet in aws_subnet.public : az => subnet.id
  }
}

output "private_subnet_ids" {
  description = "Identifiers of the private subnets keyed by availability zone."
  value = {
    for az, subnet in aws_subnet.private : az => subnet.id
  }
}

output "public_subnet_cidrs" {
  description = "CIDR blocks assigned to public subnets keyed by availability zone."
  value = {
    for az, subnet in aws_subnet.public : az => subnet.cidr_block
  }
}

output "private_subnet_cidrs" {
  description = "CIDR blocks assigned to private subnets keyed by availability zone."
  value = {
    for az, subnet in aws_subnet.private : az => subnet.cidr_block
  }
}

output "public_route_table_id" {
  description = "Identifier of the shared public route table."
  value       = aws_route_table.public.id
}

output "private_route_table_id" {
  description = "Identifier of the shared private route table."
  value       = aws_route_table.private.id
}

output "security_kms_key_arn" {
  description = "ARN of the KMS key used for security telemetry and audit encryption."
  value       = aws_kms_key.security.arn
}

output "security_kms_alias" {
  description = "Alias assigned to the security KMS key."
  value       = aws_kms_alias.security.name
}

output "vpc_flow_logs_log_group_name" {
  description = "CloudWatch log group name for VPC Flow Logs."
  value       = aws_cloudwatch_log_group.vpc_flow_logs.name
}

output "cloudtrail_log_group_name" {
  description = "CloudWatch log group name used by CloudTrail."
  value       = aws_cloudwatch_log_group.cloudtrail.name
}

output "cloudtrail_bucket_name" {
  description = "Name of the S3 bucket that stores CloudTrail logs."
  value       = aws_s3_bucket.cloudtrail.bucket
}

output "cloudtrail_bucket_arn" {
  description = "ARN of the S3 bucket that stores CloudTrail logs."
  value       = aws_s3_bucket.cloudtrail.arn
}

output "cloudtrail_arn" {
  description = "ARN of the organization audit trail."
  value       = aws_cloudtrail.audit.arn
}

output "cloudtrail_home_region" {
  description = "Home region of the CloudTrail trail."
  value       = aws_cloudtrail.audit.home_region
}

output "default_resource_tags" {
  description = "Resolved governance tags applied through the AWS provider default_tags block."
  value = merge(var.resource_tags, {
    Project              = var.project_name
    Environment          = var.environment
    ComplianceFramework  = "GDPR"
    ContainsPersonalData = tostring(var.contains_personal_data)
    DataClassification   = var.data_classification
  })
}
