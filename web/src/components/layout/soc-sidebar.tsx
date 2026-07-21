"use client";

import { motion } from "framer-motion";
import { BookOpen, BrainCircuit, ChevronLeft, ChevronRight, Radar, ShieldAlert, Target, TowerControl, Waypoints } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const navItems = [
  { key: "overview", label: "SOC Overview", icon: TowerControl },
  { key: "incidents", label: "Live Incidents", icon: ShieldAlert },
  { key: "intel", label: "Threat Intel", icon: Radar },
  { key: "assets", label: "Assets", icon: Waypoints },
  { key: "learning", label: "Learning Center", icon: BookOpen },
  { key: "charlie", label: "AI Charlie Analyst", icon: BrainCircuit },
  { key: "ranking", label: "Defense Ranking", icon: Target },
] as const;

export type SocTab = (typeof navItems)[number]["key"];

interface SocSidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  activeTab: SocTab;
  onSelectTab: (tab: SocTab) => void;
}

export function SocSidebar({ collapsed, onToggle, activeTab, onSelectTab }: SocSidebarProps) {
  return (
    <motion.aside
      animate={{ width: collapsed ? 92 : 280 }}
      transition={{ type: "spring", stiffness: 280, damping: 30 }}
      className="sticky top-0 h-screen border-r border-white/10 bg-slate-950/95 p-3"
    >
      <div className="mb-4 flex items-center justify-between">
        <div className={cn("font-semibold tracking-wide text-cyan-300", collapsed && "text-xs")}>
          {collapsed ? "SEC" : "SECUREX COMMAND"}
        </div>
        <Button variant="outline" size="icon-sm" onClick={onToggle}>
          {collapsed ? <ChevronRight /> : <ChevronLeft />}
        </Button>
      </div>

      <div className="space-y-1.5">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = activeTab === item.key;
          return (
            <button
              key={item.key}
              className={cn(
                "flex w-full items-center gap-2 rounded-xl border px-3 py-2 text-left text-sm transition-all",
                active ? "border-cyan-400/60 bg-cyan-500/10 text-cyan-200" : "border-transparent bg-slate-900/40 text-slate-300 hover:border-slate-600 hover:text-slate-100",
              )}
              onClick={() => onSelectTab(item.key)}
              type="button"
            >
              <Icon className="h-4 w-4 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </button>
          );
        })}
      </div>
    </motion.aside>
  );
}

