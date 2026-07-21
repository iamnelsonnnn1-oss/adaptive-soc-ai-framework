import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ThreatIntelItem } from "@/lib/types";

interface ThreatIntelProps {
  intel: ThreatIntelItem[];
}

export function ThreatIntel({ intel }: ThreatIntelProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Threat Intel</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {intel.map((item) => (
          <div key={item.id} className="rounded-xl border border-white/10 bg-slate-900/50 p-3">
            <div className="mb-1 flex items-center justify-between">
              <p className="text-xs font-medium uppercase tracking-wide text-violet-300">{item.source}</p>
              <span className="text-xs text-slate-400">Confidence {item.confidence}%</span>
            </div>
            <p className="text-sm text-slate-200">{item.summary}</p>
            <a href={item.referenceUrl} target="_blank" rel="noreferrer" className="mt-3 inline-flex">
              <Button variant="outline" size="sm">Open source brief</Button>
            </a>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
