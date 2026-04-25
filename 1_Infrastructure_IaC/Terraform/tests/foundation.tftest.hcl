mock_provider "aws" {
  override_data {
    target = data.aws_availability_zones.available
    values = {
      names = ["eu-central-1a", "eu-central-1b", "eu-central-1c"]
    }
  }

  override_data {
    target = data.aws_caller_identity.current
    values = {
      account_id = "123456789012"
      arn        = "arn:aws:iam::123456789012:user/test-runner"
      user_id    = "AIDATESTRUNNER1234"
    }
  }

  override_data {
    target = data.aws_partition.current
    values = {
      partition = "aws"
    }
  }

  override_data {
    target = data.aws_iam_policy_document.kms
    values = {
      json = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"EnableRootPermissions\",\"Effect\":\"Allow\",\"Action\":\"kms:*\",\"Resource\":\"*\",\"Principal\":{\"AWS\":\"arn:aws:iam::123456789012:root\"}}]}"
    }
  }

  override_data {
    target = data.aws_iam_policy_document.cloudtrail_bucket
    values = {
      json = "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"AllowCloudTrailWrite\",\"Effect\":\"Allow\",\"Action\":\"s3:PutObject\",\"Resource\":\"arn:aws:s3:::adaptive-soc-ai-framework-production-cloudtrail-123456789012/AWSLogs/123456789012/*\",\"Principal\":{\"Service\":\"cloudtrail.amazonaws.com\"}}]}"
    }
  }
}

run "foundation_defaults_plan" {
  command = plan

  assert {
    condition     = aws_vpc.core.cidr_block == "10.42.0.0/16"
    error_message = "The default VPC CIDR should stay aligned with the secure baseline."
  }

  assert {
    condition     = length(aws_subnet.public) == 2 && length(aws_subnet.private) == 2
    error_message = "The default regional footprint should create two public and two private subnets."
  }

  assert {
    condition     = aws_cloudtrail.audit.enable_log_file_validation
    error_message = "CloudTrail must keep log file validation enabled."
  }

  assert {
    condition     = aws_s3_bucket_public_access_block.cloudtrail.block_public_acls && aws_s3_bucket_public_access_block.cloudtrail.block_public_policy
    error_message = "The CloudTrail bucket must block public access."
  }

  assert {
    condition     = aws_kms_key.security.enable_key_rotation
    error_message = "The security KMS key must enable rotation."
  }
}

run "foundation_three_az_plan" {
  command = plan

  variables {
    availability_zone_count = 3
  }

  assert {
    condition     = length(aws_subnet.public) == 3 && length(aws_subnet.private) == 3
    error_message = "Three-AZ mode should create three public and three private subnets."
  }

  assert {
    condition     = aws_nat_gateway.core.subnet_id == aws_subnet.public["eu-central-1a"].id
    error_message = "The NAT gateway should be anchored in the first public subnet."
  }
}
