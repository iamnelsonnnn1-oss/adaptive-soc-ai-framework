import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { LearningModule } from "@/lib/types";

interface LearningCenterProps {
  modules: LearningModule[];
  onStartModule: (module: LearningModule) => void;
}

export function LearningCenter({ modules, onStartModule }: LearningCenterProps) {
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
            <Button className="mt-3" variant="outline" size="sm" onClick={() => onStartModule(module)}>
              Start module
            </Button>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
