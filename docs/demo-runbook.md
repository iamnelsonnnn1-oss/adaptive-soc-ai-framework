# Demo Runbook

This runbook demonstrates that the Adaptive SOC AI Framework works as a validated infrastructure-and-automation baseline before any organization-specific customization is added.

## Demo Goals

The demo proves four things:

1. Terraform foundation code is linted, validated, and testable.
2. The Terraform AWS tagging model establishes a stable contract for downstream automation.
3. Ansible can consume that contract through a dynamic AWS inventory design.
4. The full flow is reproducible locally and in GitHub Actions.

## Demo Sequence

### 1. Validate the Terraform foundation

```bash
make terraform-check
make terraform-test
```

What this proves:

- Terraform formatting is clean.
- The configuration is structurally valid.
- TFLint passes.
- Terraform tests confirm the expected network and audit baseline behavior.

### 2. Demonstrate the Ansible handoff contract

```bash
make ansible-deps
make ansible-demo
make ansible-syntax
```

What this proves:

- The Ansible controller dependencies resolve correctly.
- The mocked inventory mirrors the Terraform governance tags and AWS grouping strategy.
- The first bootstrap playbook is syntactically valid and ready for real hosts.

### 3. Show the complete local quality gate

```bash
make demo
```

This runs the same Terraform and Ansible checks that underpin the out-of-the-box framework story.

## Live AWS Handoff

The repository includes two Ansible inventory modes:

- `1_Infrastructure_IaC/Ansible/inventory/demo.mock.yml`
  Use this for CI and demos without live AWS compute.
- `1_Infrastructure_IaC/Ansible/inventory/production.aws_ec2.yml`
  Use this when real EC2 instances exist in AWS with the Terraform-managed tags:
  - `Project=adaptive-soc-ai-framework`
  - `Environment=production`
  - `ManagedBy=Terraform`
  - `ComplianceFramework=GDPR`

## Buyer Narrative

The framework is meant to be shown in two phases:

1. Baseline functionality
   The platform provisions a secure AWS foundation, validates cleanly, and demonstrates automation readiness.
2. Organizational customization
   The same framework is then adapted to the client’s specific identity model, tooling stack, SIEM/SOAR choices, environments, and operational controls.

That sequence matters. Buyers should see a working framework first and customization second.
