import Link from "next/link";

import { AiCharlieChat } from "@/components/soc/ai-charlie-chat";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { listThreats } from "@/lib/services/threat-service";

export default function AiCharliePage() {
  const threats = listThreats();
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-950 to-slate-900 p-6 text-slate-100">
      <div className="mx-auto max-w-6xl space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-cyan-200">AI Charlie Analyst · Conversational Triage Lab</h1>
          <Link href="/" className={buttonVariants({ variant: "outline" })}>Back to SOC cockpit</Link>
        </div>
        <div className="grid gap-4 lg:grid-cols-[1.2fr_1fr]">
          <AiCharlieChat selectedThreat={threats[0]} />
          <Card>
            <CardHeader><CardTitle>Training Context</CardTitle></CardHeader>
            <CardContent className="space-y-2 text-sm text-slate-300">
              <p>This mock page isolates analyst coaching for enterprise training simulations.</p>
              <p>Service layer is mock-first and designed for future API integration.</p>
              <p>Suggested prompts:</p>
              <ul className="list-disc space-y-1 pl-4 text-slate-400">
                <li>Classify this incident with MITRE ATT&CK mapping.</li>
                <li>Map immediate actions to NIST CSF phases.</li>
                <li>Give a three-step containment and recovery plan.</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}
