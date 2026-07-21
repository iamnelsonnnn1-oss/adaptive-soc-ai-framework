import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getRankFromXp } from "@/lib/services/progression-service";

interface RankProgressProps {
  xp: number;
}

export function RankProgress({ xp }: RankProgressProps) {
  const rank = getRankFromXp(xp);
  return (
    <Card>
      <CardHeader>
        <CardTitle>Defense Progression</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-slate-300">Current rank: <span className="font-medium text-cyan-300">{rank.current.name}</span></p>
        <p className="mt-1 text-xs text-slate-400">Next rank: {rank.next.name}</p>
        <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-800">
          <div className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-violet-400" style={{ width: `${Math.round(rank.progress * 100)}%` }} />
        </div>
        <p className="mt-2 text-xs text-slate-400">{xp} XP</p>
      </CardContent>
    </Card>
  );
}

