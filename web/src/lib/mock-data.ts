import type { Asset, LearningModule, RankTier, Threat, ThreatIntelItem } from "@/lib/types";

export const mockThreats: Threat[] = [
  {
    id: "THR-1001",
    title: "Credential stuffing against SSO gateway",
    description: "High-frequency authentication attempts from rotating IP ranges.",
    severity: "critical",
    status: "triaging",
    category: "credential_theft",
    sourceIp: "185.217.0.14",
    targetAsset: "auth-gateway-01",
    mitreTactic: "TA0006 Credential Access",
    confidence: 96,
    nistFunction: "Detect",
    detectedAt: "2026-07-18T05:35:00Z",
  },
  {
    id: "THR-1002",
    title: "Lateral movement over SMB",
    description: "Unusual east-west traffic from HR subnet to finance server.",
    severity: "high",
    status: "investigating",
    category: "lateral_movement",
    sourceIp: "10.18.44.12",
    targetAsset: "finance-files-03",
    mitreTactic: "TA0008 Lateral Movement",
    confidence: 88,
    nistFunction: "Respond",
    detectedAt: "2026-07-18T06:10:00Z",
  },
  {
    id: "THR-1003",
    title: "Suspicious OAuth token replay",
    description: "Bearer token used from two distant geographies within 2 minutes.",
    severity: "high",
    status: "new",
    category: "privilege_escalation",
    sourceIp: "91.240.118.77",
    targetAsset: "iam-control-plane",
    mitreTactic: "TA0004 Privilege Escalation",
    confidence: 91,
    nistFunction: "Protect",
    detectedAt: "2026-07-18T07:05:00Z",
  },
  {
    id: "THR-1004",
    title: "Potential command-and-control beaconing",
    description: "Periodic encrypted egress with beacon interval pattern.",
    severity: "medium",
    status: "new",
    category: "zero_day",
    sourceIp: "203.0.113.34",
    targetAsset: "proxy-egress-01",
    mitreTactic: "TA0011 Command & Control",
    confidence: 79,
    nistFunction: "Identify",
    detectedAt: "2026-07-18T08:20:00Z",
  },
  {
    id: "THR-1005",
    title: "Data staging before exfiltration",
    description: "Large archive file created and moved to cloud sync bucket.",
    severity: "medium",
    status: "remediated",
    category: "data_exfiltration",
    sourceIp: "172.16.30.7",
    targetAsset: "object-store-eu",
    mitreTactic: "TA0010 Exfiltration",
    confidence: 76,
    nistFunction: "Recover",
    detectedAt: "2026-07-18T09:10:00Z",
  },
];

export const mockThreatIntel: ThreatIntelItem[] = [
  { id: "INT-1", source: "CISA Advisory", summary: "Active exploitation of identity provider vulnerabilities.", confidence: 92 },
  { id: "INT-2", source: "MITRE CTI", summary: "Increased abuse of OAuth token theft in phishing clusters.", confidence: 84 },
  { id: "INT-3", source: "Vendor SOC Feed", summary: "Ransomware affiliates pivoting with SMB spray-and-pray tactics.", confidence: 81 },
];

export const mockAssets: Asset[] = [
  { id: "AST-1", name: "auth-gateway-01", owner: "Identity Team", risk: "critical", status: "degraded" },
  { id: "AST-2", name: "finance-files-03", owner: "Finance IT", risk: "high", status: "degraded" },
  { id: "AST-3", name: "proxy-egress-01", owner: "Network Ops", risk: "medium", status: "healthy" },
  { id: "AST-4", name: "object-store-eu", owner: "Platform", risk: "medium", status: "healthy" },
];

export const mockLearningModules: LearningModule[] = [
  { id: "LM-1", title: "Credential Stuffing Triage Drill", stage: "Sentinel Initiate", xpReward: 120 },
  { id: "LM-2", title: "Lateral Movement Hunt", stage: "Threat Analyst", xpReward: 180 },
  { id: "LM-3", title: "Containment Orchestration Exercise", stage: "SOC Operator", xpReward: 240 },
  { id: "LM-4", title: "Cross-team Incident Command", stage: "Incident Commander", xpReward: 320 },
  { id: "LM-5", title: "Adaptive Detection Engineering", stage: "Digital Sovereign", xpReward: 450 },
];

export const rankTiers: RankTier[] = [
  { name: "Sentinel Initiate", minXp: 0 },
  { name: "Threat Analyst", minXp: 300 },
  { name: "SOC Operator", minXp: 800 },
  { name: "Incident Commander", minXp: 1500 },
  { name: "Digital Sovereign", minXp: 3000 },
];

