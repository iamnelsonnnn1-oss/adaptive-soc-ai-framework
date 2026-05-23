#!/usr/bin/env bash
set -euo pipefail

for overlay in demo staging production; do
  echo "Validating overlay: ${overlay}"
  kubectl kustomize "1_Infrastructure_IaC/Kubernetes/overlays/${overlay}" >/dev/null
done
