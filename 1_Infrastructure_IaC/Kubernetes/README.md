# Kubernetes Orchestration

This directory contains the initial Kubernetes migration structure for the Adaptive SOC AI Framework.

The first orchestrated workload is `soc-demo-service`, which mirrors the validated Docker demo service and provides the safest path into Kubernetes without disrupting the Terraform, Ansible, and Docker baseline.

## Layout

- `base/`: shared namespace and foundational policies
- `apps/`: workload-specific manifests
- `overlays/`: environment-specific Kustomize overlays
- `policies/`: reusable security posture references
- `ci/`: manifest validation helpers for local and CI execution

## Initial Scope

The current Kubernetes phase focuses on:

- `Namespace`
- `Deployment`
- `Service`
- `ConfigMap`
- `PodDisruptionBudget`
- Kustomize overlays for `demo`, `staging`, and `production`

Future components such as Suricata sensors, external connector services, ingress, autoscaling, and secret backends should extend this structure rather than replace it.
