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
import type { Threat } from "@/lib/types";

export function SocShell() {
  const [collapsed, setCollapsed] = useState(false);
  const [activeTab, setActiveTab] = useState<SocTab>("overview");
  const [selectedThreat, setSelectedThreat] = useState<Threat | undefined>(listThreats()[0]);

  const incidents = useMemo(() => listThreats(), []);
  const criticalCount = countBySeverity(incidents, "critical");
  const remediated = incidents.filter((t) => t.status === "remediated" || t.status === "closed").length;
  const defcon = criticalCount >= 2 ? "DEFCON 2" : "DEFCON 4";

  return (
    <div className="flex min-h-screen bg-gradient-to-b from-slate-950 via-slate-950 to-slate-900 text-slate-100">
      <SocSidebar collapsed={collapsed} onToggle={() => setCollapsed((v) => !v)} activeTab={activeTab} onSelectTab={setActiveTab} />
      <main className="flex-1 p-4 md:p-6">
        <div className="mx-auto max-w-[1400px] space-y-4">
          <SocHeader defcon={defcon} />
          <OverviewCards activeThreats={incidents.length} critical={criticalCount} remediated={remediated} mttr={19} />
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
            {activeTab === "overview" && (
              <div className="grid gap-4 xl:grid-cols-[1.2fr_1fr]">
                <LiveIncidents incidents={incidents} selectedId={selectedThreat?.id} onSelectIncident={setSelectedThreat} />
                <IncidentDetail threat={selectedThreat} />
              </div>
            )}
            {activeTab === "incidents" && (
              <div className="grid gap-4 xl:grid-cols-[1.2fr_1fr]">
                <LiveIncidents incidents={incidents} selectedId={selectedThreat?.id} onSelectIncident={setSelectedThreat} />
                <AiCharlieChat selectedThreat={selectedThreat} />
              </div>
            )}
            {activeTab === "intel" && <ThreatIntel intel={mockThreatIntel} />}
            {activeTab === "assets" && <AssetsPanel assets={mockAssets} />}
            {activeTab === "learning" && <LearningCenter modules={mockLearningModules} />}
            {activeTab === "charlie" && (
              <div className="space-y-3">
                <AiCharlieChat selectedThreat={selectedThreat} />
                <Link href="/ai-charlie" className={buttonVariants({ variant: "outline" })}>
                  Open full AI Charlie analyst page
                </Link>
              </div>
            )}
            {activeTab === "ranking" && <RankProgress xp={1040} />}
          </motion.div>
        </div>
      </main>
    </div>
  );
}
