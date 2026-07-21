import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Threat } from "@/lib/types";

interface IncidentDetailProps {
  threat?: Threat;
}

export function IncidentDetail({ threat }: IncidentDetailProps) {
  if (!threat) {
    return (
      <Card>
        <CardHeader><CardTitle>Incident Detail</CardTitle></CardHeader>
        <CardContent><p className="text-sm text-slate-400">Select an incident to begin triage training.</p></CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{threat.title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 text-sm">
        <p className="text-slate-300">{threat.description}</p>
        <p className="text-slate-400">Severity: <span className="text-slate-200">{threat.severity}</span> · Status: <span className="text-slate-200">{threat.status}</span></p>
        <p className="text-slate-400">MITRE: <span className="text-slate-200">{threat.mitreTactic}</span></p>
        <p className="text-slate-400">NIST: <span className="text-slate-200">{threat.nistFunction}</span></p>
        <p className="text-slate-400">Source: <span className="text-slate-200">{threat.sourceIp}</span> → Target: <span className="text-slate-200">{threat.targetAsset}</span></p>
      </CardContent>
    </Card>
  );
}

