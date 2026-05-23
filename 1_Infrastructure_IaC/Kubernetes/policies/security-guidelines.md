# Kubernetes Security Guidelines

- Prefer non-root containers.
- Drop all Linux capabilities unless explicitly required.
- Use readiness and liveness probes for workload validation.
- Keep secrets out of ConfigMaps and out of the repository.
- Use overlays for environment-specific scaling and resource adjustments.
- Add NetworkPolicies before exposing new workloads.
