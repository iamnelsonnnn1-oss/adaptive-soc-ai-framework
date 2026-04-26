TF_DIR := 1_Infrastructure_IaC/Terraform
ANSIBLE_DIR := 1_Infrastructure_IaC/Ansible
ANSIBLE_CONFIG := $(CURDIR)/$(ANSIBLE_DIR)/ansible.cfg

.PHONY: terraform-check terraform-test ansible-deps ansible-demo ansible-syntax demo ci-local

terraform-check:
	terraform -chdir=$(TF_DIR) fmt -check
	terraform -chdir=$(TF_DIR) validate
	tflint --chdir=$(TF_DIR)

terraform-test:
	terraform -chdir=$(TF_DIR) test

ansible-deps:
	ANSIBLE_CONFIG=$(ANSIBLE_CONFIG) ansible-galaxy collection install -r $(ANSIBLE_DIR)/collections/requirements.yml

ansible-demo:
	ANSIBLE_CONFIG=$(ANSIBLE_CONFIG) ansible-inventory -i $(ANSIBLE_DIR)/inventory/demo.mock.yml --graph
	ANSIBLE_CONFIG=$(ANSIBLE_CONFIG) ansible-playbook -i $(ANSIBLE_DIR)/inventory/demo.mock.yml $(ANSIBLE_DIR)/playbooks/validate_handoff_contract.yml

ansible-syntax:
	ANSIBLE_CONFIG=$(ANSIBLE_CONFIG) ansible-playbook -i $(ANSIBLE_DIR)/inventory/demo.mock.yml $(ANSIBLE_DIR)/playbooks/validate_inventory.yml --syntax-check
	ANSIBLE_CONFIG=$(ANSIBLE_CONFIG) ansible-playbook -i $(ANSIBLE_DIR)/inventory/demo.mock.yml $(ANSIBLE_DIR)/playbooks/bootstrap_linux.yml --syntax-check

demo: terraform-check terraform-test ansible-demo ansible-syntax

ci-local: terraform-check terraform-test ansible-syntax ansible-demo
