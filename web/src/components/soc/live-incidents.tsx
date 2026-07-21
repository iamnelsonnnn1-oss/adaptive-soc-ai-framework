import { motion } from "framer-motion";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Severity, Threat } from "@/lib/types";
import { cn } from "@/lib/utils";

const severityClass: Record<Severity, string> = {
  critical: "bg-red-500/20 text-red-300 border-red-400/50",
  high: "bg-orange-500/20 text-orange-300 border-orange-400/50",
  medium: "bg-amber-500/20 text-amber-300 border-amber-400/50",
  low: "bg-sky-500/20 text-sky-300 border-sky-400/50",
  info: "bg-slate-500/20 text-slate-300 border-slate-400/50",
};

interface LiveIncidentsProps {
  incidents: Threat[];
  selectedId?: string;
  onSelectIncident: (incident: Threat) => void;
}

export function LiveIncidents({ incidents, selectedId, onSelectIncident }: LiveIncidentsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Live Incidents</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {incidents.map((incident) => (
          <motion.button
            key={incident.id}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            className={cn(
              "w-full rounded-xl border p-3 text-left transition-all",
              selectedId === incident.id ? "border-cyan-400/70 bg-cyan-500/10" : "border-white/10 bg-slate-900/50 hover:border-slate-500",
            )}
            onClick={() => onSelectIncident(incident)}
            type="button"
          >
            <div className="mb-1 flex items-center justify-between">
              <span className={cn("rounded-full border px-2 py-0.5 text-xs font-medium uppercase", severityClass[incident.severity])}>{incident.severity}</span>
              <span className="text-xs text-slate-400">{new Date(incident.detectedAt).toLocaleString()}</span>
            </div>
            <p className="text-sm font-medium text-slate-100">{incident.title}</p>
            <p className="text-xs text-slate-400">{incident.sourceIp} → {incident.targetAsset}</p>
          </motion.button>
        ))}
      </CardContent>
    </Card>
  );
}

