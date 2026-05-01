import { Activity, AlertTriangle, Map, Radar } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { GapCard } from "@/components/gap-card";
import { SiteShell } from "@/components/site-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const SAMPLE_GAPS = [
  {
    title: "No mention of decaf availability across cold-brew SKUs",
    type: "missing_node" as const,
    severity: 0.82,
    revenueAtRisk: 4200,
    calibration: "confident" as const,
    affectedProducts: 7,
  },
  {
    title: "Return window contradicts FAQ vs. policy page",
    type: "contradiction" as const,
    severity: 0.71,
    revenueAtRisk: 2800,
    calibration: "certain" as const,
    affectedProducts: 24,
  },
  {
    title: "Llama-3.3 mis-states origin for Single-Origin Ethiopia",
    type: "agent_misread" as const,
    severity: 0.63,
    revenueAtRisk: 1900,
    calibration: "uncertain" as const,
    affectedProducts: 1,
  },
] as const;

export default function AuditPage({ params }: { params: { storeId: string } }): JSX.Element {
  return (
    <SiteShell>
      <header className="mb-6 space-y-1">
        <p className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
          /audit/{params.storeId}
        </p>
        <h1 className="text-2xl font-bold tracking-tight">AI Readiness Audit</h1>
      </header>

      <section className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">
              AI Readiness Score
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="font-mono text-3xl font-bold">--</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">
              Tacit Knowledge Capture
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="font-mono text-3xl font-bold">--%</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">
              Agent Coverage
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="font-mono text-3xl font-bold">--%</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">
              Last audit
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="font-mono text-sm">never</div>
          </CardContent>
        </Card>
      </section>

      <div className="grid grid-cols-12 gap-4">
        <section className="col-span-12 space-y-3 lg:col-span-8">
          <div className="flex items-center justify-between">
            <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              <AlertTriangle className="h-4 w-4" aria-hidden />
              Ranked gaps
            </h2>
            <span className="font-mono text-xs text-muted-foreground">
              sample · coming Day 7
            </span>
          </div>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            {SAMPLE_GAPS.map((g) => (
              <GapCard key={g.title} {...g} />
            ))}
          </div>
        </section>
        <aside className="col-span-12 space-y-4 lg:col-span-4">
          <EmptyState
            icon={Radar}
            title="AI Readiness Radar"
            description="5 axes: catalog clarity · policy completeness · FAQ coverage · trust signals · edge cases."
            className="h-[280px]"
          />
          <EmptyState
            icon={Map}
            title="Coverage heatmap"
            description="Treemap colored green / yellow / red - which categories are well-represented vs. dark zones."
            className="h-[260px]"
          />
        </aside>
      </div>
      <div className="mt-6 flex items-center gap-2 text-xs text-muted-foreground">
        <Activity className="h-3.5 w-3.5" aria-hidden />
        <span className="font-mono">audit dashboard - coming Day 7</span>
      </div>
    </SiteShell>
  );
}
