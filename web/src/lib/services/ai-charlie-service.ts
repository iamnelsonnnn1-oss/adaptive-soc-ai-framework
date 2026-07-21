import type { Threat } from "@/lib/types";

export function respondAsKai(question: string, selectedThreat?: Threat): string {
  const q = question.toLowerCase();
  if (q.includes("landscape") || q.includes("active threat")) {
    return "### Threat Landscape\nPrioritize critical and high incidents first, confirm blast radius, then sequence containment by business impact.";
  }

  if (!selectedThreat) {
    return "### Triage Context\nNo incident selected. Open a live incident first, then I can map MITRE ATT&CK, NIST, and remediation steps.";
  }

  return [
    "### Classification",
    `- Threat: ${selectedThreat.category}`,
    `- MITRE: ${selectedThreat.mitreTactic}`,
    "",
    "### Why this matters",
    `- Adversary intent appears to target ${selectedThreat.targetAsset} and persistence opportunities.`,
    "",
    "### NIST mapping",
    `- Primary function: ${selectedThreat.nistFunction}`,
    "",
    "### Ordered remediation",
    "1. Contain identity/host and preserve evidence.",
    "2. Hunt adjacent indicators across endpoint and SIEM.",
    "3. Validate eradication and harden detection.",
    "",
    "### Learning tip",
    "Map each remediation action back to one ATT&CK tactic to improve future detections.",
  ].join("\n");
}

