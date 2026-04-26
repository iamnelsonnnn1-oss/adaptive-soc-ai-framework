# Ansible Handoff

This Ansible directory is wired to the Terraform AWS foundation through the `amazon.aws.aws_ec2` dynamic inventory plugin.

The inventory source is aligned with the validated Terraform defaults:

- Region: `eu-central-1`
- Project tag: `adaptive-soc-ai-framework`
- Environment tag: `production`
- Managed-by tag: `Terraform`
- Compliance tag: `GDPR`

## Usage

Install the required Ansible collection:

```bash
ansible-galaxy collection install -r collections/requirements.yml
```

List the discovered hosts:

```bash
ansible-inventory -i inventory/production.aws_ec2.yml --graph
```

List the demo inventory used for CI-safe handoff validation:

```bash
ansible-inventory -i inventory/demo.mock.yml --graph
```

Run an ad hoc command:

```bash
ansible all -m ping
```

Validate the Terraform-to-Ansible handoff:

```bash
ansible-playbook playbooks/validate_inventory.yml
```

Validate the demo handoff contract without live AWS resources:

```bash
ansible-playbook -i inventory/demo.mock.yml playbooks/validate_handoff_contract.yml
```

Run the first baseline bootstrap playbook:

```bash
ansible-playbook playbooks/bootstrap_linux.yml
```

## Notes

The current Terraform layer provisions network and audit foundations, but not EC2 instances yet. Until compute resources exist with the matching Terraform tags, the dynamic inventory is expected to return an empty host set.

For CI and demos, `inventory/demo.mock.yml` simulates the host metadata that the AWS dynamic inventory plugin is expected to resolve from Terraform-managed infrastructure.
