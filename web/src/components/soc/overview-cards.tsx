import { Activity, AlertTriangle, CheckCircle2, Clock4 } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface OverviewCardsProps {
  activeThreats: number;
  critical: number;
  remediated: number;
  mttr: number;
}

export function OverviewCards({ activeThreats, critical, remediated, mttr }: OverviewCardsProps) {
  const cards = [
    { title: "Active Threats", value: activeThreats, icon: Activity, color: "text-cyan-300" },
    { title: "Critical", value: critical, icon: AlertTriangle, color: "text-red-300" },
    { title: "Remediated", value: remediated, icon: CheckCircle2, color: "text-emerald-300" },
    { title: "MTTR (min)", value: mttr, icon: Clock4, color: "text-amber-300" },
  ];

  return (
    <section className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>{card.title}</CardTitle>
            <card.icon className={`h-4 w-4 ${card.color}`} />
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-semibold text-slate-100">{card.value}</p>
          </CardContent>
        </Card>
      ))}
    </section>
  );
}

