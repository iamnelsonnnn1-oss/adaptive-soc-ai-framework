import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Asset } from "@/lib/types";

interface AssetsPanelProps {
  assets: Asset[];
}

export function AssetsPanel({ assets }: AssetsPanelProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Assets</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {assets.map((asset) => (
          <div key={asset.id} className="flex items-center justify-between rounded-xl border border-white/10 bg-slate-900/50 px-3 py-2 text-sm">
            <div>
              <p className="font-medium text-slate-100">{asset.name}</p>
              <p className="text-xs text-slate-400">{asset.owner}</p>
            </div>
            <div className="text-right">
              <p className="text-xs uppercase text-slate-300">{asset.risk} risk</p>
              <p className="text-xs text-slate-400">{asset.status}</p>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

