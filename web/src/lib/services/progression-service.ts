import { rankTiers } from "@/lib/mock-data";

export function getRankFromXp(xp: number) {
  const tiers = [...rankTiers];
  let current = tiers[0];
  let next = tiers[1] ?? tiers[0];

  for (let i = 0; i < tiers.length; i += 1) {
    if (xp >= tiers[i].minXp) {
      current = tiers[i];
      next = tiers[i + 1] ?? tiers[i];
    }
  }

  const denominator = Math.max(1, next.minXp - current.minXp);
  const progress = next === current ? 1 : Math.min(1, Math.max(0, (xp - current.minXp) / denominator));

  return { current, next, progress };
}

