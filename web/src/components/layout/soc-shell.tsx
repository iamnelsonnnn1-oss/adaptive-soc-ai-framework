"use client";

import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";

import { SocHeader } from "@/components/layout/soc-header";
import { SocSidebar, type SocTab } from "@/components/layout/soc-sidebar";
import { AiCharlieChat } from "@/components/soc/ai-charlie-chat";
import { AssetsPanel } from "@/components/soc/assets-panel";
import { IncidentDetail } from "@/components/soc/incident-detail";
import { LearningCenter } from "@/components/soc/learning-center";
import { LiveIncidents } from "@/components/soc/live-incidents";
import { OverviewCards } from "@/components/soc/overview-cards";
import { RankProgress } from "@/components/soc/rank-progress";
import { ThreatIntel } from "@/components/soc/threat-intel";
import { buttonVariants } from "@/components/ui/button";
import { mockAssets, mockLearningModules, mockThreatIntel } from "@/lib/mock-data";
import { countBySeverity, listThreats } from "@/lib/services/threat-service";
import type { LearningModule, Threat } from "@/lib/types";

export function SocShell() {
  const [collapsed, setCollapsed] = useState(false);
  const [activeTab, setActiveTab] = useState<SocTab>("overview");
  const [incidents, setIncidents] = useState<Threat[]>(() => listThreats());
  const [selectedThreatId, setSelectedThreatId] = useState<string | undefined>(listThreats()[0]?.id);
  const [xp, setXp] = useState(1040);
  const [uiNotice, setUiNotice] = useState("Every action in this workspace is wired for training flow.");

  const selectedThreat = useMemo(
    () => incidents.find((incident) => incident.id === selectedThreatId),
    [incidents, selectedThreatId],
  );
  const criticalCount = countBySeverity(incidents, "critical");
  const remediated = incidents.filter((t) => t.status === "remediated" || t.status === "closed").length;
  const defcon = criticalCount >= 2 ? "DEFCON 2" : "DEFCON 4";

  const handleSelectIncident = (incident: Threat) => {
    setSelectedThreatId(incident.id);
    setUiNotice(`Selected ${incident.id}. You can now open guided triage, MITRE, and NIST actions.`);
  };

  const handleMarkRemediated = (threatId: string) => {
    let updated = false;
    setIncidents((current) =>
      current.map((incident) => {
        if (incident.id !== threatId) return incident;
        if (incident.status === "remediated" || incident.status === "closed") return incident;
        updated = true;
        return { ...incident, status: "remediated" };
      }),
    );
    if (updated) {
      setXp((value) => value + 120);
      setUiNotice(`${threatId} marked remediated. +120 XP awarded.`);
    } else {
      setUiNotice(`${threatId} is already remediated.`);
    }
  };

  const handleOpenCharlie = () => {
    setActiveTab("charlie");
    setUiNotice("AI Charlie guidance opened for the selected incident.");
  };

  const handleStartModule = (module: LearningModule) => {
    setXp((value) => value + module.xpReward);
    setActiveTab("ranking");
    setUiNotice(`Started ${module.title}. +${module.xpReward} XP awarded.`);
  };

  return (
    <div className="flex min-h-screen bg-gradient-to-b from-slate-950 via-slate-950 to-slate-900 text-slate-100">
      <SocSidebar collapsed={collapsed} onToggle={() => setCollapsed((v) => !v)} activeTab={activeTab} onSelectTab={setActiveTab} />
      <main className="flex-1 p-4 md:p-6">
        <div className="mx-auto max-w-[1400px] space-y-4">
          <SocHeader defcon={defcon} />
          <OverviewCards activeThreats={incidents.length} critical={criticalCount} remediated={remediated} mttr={19} />
          <div className="rounded-xl border border-cyan-400/30 bg-cyan-500/10 px-3 py-2 text-sm text-cyan-100">
            {uiNotice}
          </div>
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
            {activeTab === "overview" && (
              <div className="grid gap-4 xl:grid-cols-[1.2fr_1fr]">
                <LiveIncidents incidents={incidents} selectedId={selectedThreat?.id} onSelectIncident={handleSelectIncident} />
                <IncidentDetail
                  threat={selectedThreat}
                  onMarkRemediated={handleMarkRemediated}
                  onOpenCharlie={handleOpenCharlie}
                />
              </div>
            )}
            {activeTab === "incidents" && (
              <div className="grid gap-4 xl:grid-cols-[1.2fr_1fr]">
                <LiveIncidents incidents={incidents} selectedId={selectedThreat?.id} onSelectIncident={handleSelectIncident} />
                <AiCharlieChat selectedThreat={selectedThreat} />
              </div>
            )}
            {activeTab === "intel" && <ThreatIntel intel={mockThreatIntel} />}
            {activeTab === "assets" && <AssetsPanel assets={mockAssets} />}
            {activeTab === "learning" && <LearningCenter modules={mockLearningModules} onStartModule={handleStartModule} />}
            {activeTab === "charlie" && (
              <div className="space-y-3">
                <AiCharlieChat selectedThreat={selectedThreat} />
                <Link href="/ai-charlie" className={buttonVariants({ variant: "outline" })}>
                  Open full AI Charlie analyst page
                </Link>
              </div>
            )}
            {activeTab === "ranking" && <RankProgress xp={xp} />}
          </motion.div>
        </div>
      </main>
    </div>
  );
}
