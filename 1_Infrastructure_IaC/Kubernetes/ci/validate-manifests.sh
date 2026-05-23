#!/usr/bin/env bash
set -euo pipefail

find 1_Infrastructure_IaC/Kubernetes -type f \( -name "*.yaml" -o -name "*.yml" \) | sort
