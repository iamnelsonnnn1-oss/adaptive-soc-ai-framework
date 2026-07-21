import { Button, buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Threat } from "@/lib/types";

interface IncidentDetailProps {
  threat?: Threat;
  onMarkRemediated: (threatId: string) => void;
  onOpenCharlie: () => void;
}

function getMitreTacticCode(tactic: string) {
  const match = tactic.match(/TA\d{4}/);
  return match?.[0];
}

export function IncidentDetail({ threat, onMarkRemediated, onOpenCharlie }: IncidentDetailProps) {
  if (!threat) {
    return (
      <Card>
        <CardHeader><CardTitle>Incident Detail</CardTitle></CardHeader>
        <CardContent><p className="text-sm text-slate-400">Select an incident to begin triage training.</p></CardContent>
      </Card>
    );
  }

  const mitreCode = getMitreTacticCode(threat.mitreTactic);
  const mitreUrl = mitreCode ? `https://attack.mitre.org/tactics/${mitreCode}/` : "https://attack.mitre.org/tactics/";

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
        <div className="grid gap-2 pt-2 sm:grid-cols-2">
          <Button variant="outline" onClick={() => onMarkRemediated(threat.id)}>
            Mark remediated
          </Button>
          <Button onClick={onOpenCharlie}>Open AI Charlie guidance</Button>
          <a href={mitreUrl} target="_blank" rel="noreferrer" className={buttonVariants({ variant: "outline", className: "w-full" })}>
            Open MITRE ATT&CK
          </a>
          <a href="https://www.nist.gov/cyberframework" target="_blank" rel="noreferrer" className={buttonVariants({ variant: "outline", className: "w-full" })}>
            Open NIST CSF
          </a>
        </div>
      </CardContent>
    </Card>
  );
}
