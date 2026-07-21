import { ShieldCheck } from "lucide-react";

interface SocHeaderProps {
  defcon: string;
}

export function SocHeader({ defcon }: SocHeaderProps) {
  return (
    <header className="rounded-2xl border border-cyan-400/30 bg-slate-900/80 p-4 shadow-xl shadow-black/25">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5 text-cyan-300" />
          <h1 className="text-lg font-semibold tracking-wide text-slate-50">Adaptive SOC AI Framework · Enterprise Cyber Range</h1>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="rounded-full border border-amber-400/60 bg-amber-500/10 px-3 py-1 text-amber-300">{defcon}</span>
          <span className="rounded-full border border-violet-400/60 bg-violet-500/10 px-3 py-1 text-violet-300">CYBER RANGE · LIVE FIRE</span>
        </div>
      </div>
    </header>
  );
}

