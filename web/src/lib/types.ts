export type Severity = "critical" | "high" | "medium" | "low" | "info";
export type IncidentStatus = "new" | "triaging" | "investigating" | "remediated" | "closed";
export type NistFunction = "Identify" | "Protect" | "Detect" | "Respond" | "Recover";

export interface Threat {
  id: string;
  title: string;
  description: string;
  severity: Severity;
  status: IncidentStatus;
  category: string;
  sourceIp: string;
  targetAsset: string;
  mitreTactic: string;
  confidence: number;
  nistFunction: NistFunction;
  detectedAt: string;
}

export interface ThreatIntelItem {
  id: string;
  source: string;
  summary: string;
  confidence: number;
  referenceUrl: string;
}

export interface Asset {
  id: string;
  name: string;
  owner: string;
  risk: "critical" | "high" | "medium" | "low";
  status: "healthy" | "degraded" | "offline";
}

export interface LearningModule {
  id: string;
  title: string;
  stage: "Sentinel Initiate" | "Threat Analyst" | "SOC Operator" | "Incident Commander" | "Digital Sovereign";
  xpReward: number;
}

export interface RankTier {
  name: "Sentinel Initiate" | "Threat Analyst" | "SOC Operator" | "Incident Commander" | "Digital Sovereign";
  minXp: number;
}
