import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { LearningModule } from "@/lib/types";

interface LearningCenterProps {
  modules: LearningModule[];
}

export function LearningCenter({ modules }: LearningCenterProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Learning Center</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {modules.map((module) => (
          <div key={module.id} className="rounded-xl border border-white/10 bg-slate-900/50 p-3">
            <p className="text-sm font-medium text-slate-100">{module.title}</p>
            <p className="text-xs text-slate-400">{module.stage} · +{module.xpReward} XP</p>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

