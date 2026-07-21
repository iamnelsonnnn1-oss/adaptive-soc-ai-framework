import { mockThreats } from "@/lib/mock-data";
import type { Severity, Threat } from "@/lib/types";

export function listThreats(): Threat[] {
  return [...mockThreats].sort((a, b) => Date.parse(a.detectedAt) - Date.parse(b.detectedAt));
}

export function filterThreats(threats: Threat[], severity: Severity | "all"): Threat[] {
  if (severity === "all") return threats;
  return threats.filter((t) => t.severity === severity);
}

export function countBySeverity(threats: Threat[], severity: Severity): number {
  return threats.filter((t) => t.severity === severity).length;
}

