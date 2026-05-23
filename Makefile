TF_DIR := 1_Infrastructure_IaC/Terraform
ANSIBLE_DIR := 1_Infrastructure_IaC/Ansible
ANSIBLE_CONFIG := $(CURDIR)/$(ANSIBLE_DIR)/ansible.cfg
DOCKER_DEMO_DIR := 1_Infrastructure_IaC/Docker/soc-demo-service

.PHONY: terraform-check terraform-test ansible-deps ansible-demo ansible-syntax docker-build docker-run docker-smoke demo ci-local

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

docker-build:
	docker build -t soc-demo-service:latest $(DOCKER_DEMO_DIR)

docker-run:
	docker run --rm -p 8080:8080 soc-demo-service:latest

docker-smoke: docker-build
	sh -c 'docker run -d --rm --name soc-demo-smoke -p 8080:8080 soc-demo-service:latest >/dev/null && trap "docker stop soc-demo-smoke >/dev/null" EXIT && sleep 5 && curl -fsS http://127.0.0.1:8080/health && curl -fsS http://127.0.0.1:8080/framework && curl -fsS http://127.0.0.1:8080/telemetry >/dev/null'

demo: terraform-check terraform-test ansible-demo ansible-syntax docker-smoke

ci-local: terraform-check terraform-test ansible-syntax ansible-demo docker-smoke
