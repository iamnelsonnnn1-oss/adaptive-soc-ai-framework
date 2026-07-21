# SecureX Command Frontend (Next.js)

Enterprise-grade educational cyber range frontend for the Adaptive SOC AI Framework.

## Stack

- Next.js (App Router)
- React + TypeScript
- Tailwind CSS
- shadcn UI patterns (`button`, `card`, utility layer)
- Framer Motion

## UX Targets Implemented

- Dark enterprise theme with rounded cards and subtle shadows
- Smooth transitions and interaction animations
- Collapsible SOC sidebar with:
  - SOC Overview
  - Live Incidents
  - Threat Intel
  - Assets
  - Learning Center
  - AI Charlie Analyst
  - Defense Ranking
- Dedicated AI Charlie analyst page (`/ai-charlie`) for conversational triage training
- Gamified progression tiers from Sentinel Initiate to Digital Sovereign

## Architecture

UI components are separated from business logic and data services.

### UI Layer

- `src/components/layout/*` → shell, header, sidebar
- `src/components/soc/*` → incidents, intel, assets, learning, AI chat, progression
- `src/components/ui/*` → shared shadcn-style primitives

### Business Logic Layer

- `src/lib/services/threat-service.ts` → threat listing/filtering/stats
- `src/lib/services/progression-service.ts` → rank progression logic
- `src/lib/services/ai-charlie-service.ts` → mock conversational triage response

### Mock Data Layer

- `src/lib/mock-data.ts` → incidents, threat intel, assets, learning modules, rank tiers
- `src/lib/types.ts` → strict domain types

## Future API Integration

The service layer is intentionally mock-first and can be replaced with live API calls without rewriting UI components.

Typical migration path:
1. Replace mock return values in `src/lib/services/*` with API clients.
2. Keep component props/contracts unchanged.
3. Add caching/query orchestration (e.g. React Query) in the service boundary.

## Local Development

```bash
cd web
npm install
npm run dev
```

Open `http://localhost:3000`.

