import { Network } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { SiteShell } from "@/components/site-shell";
import { NODE_COLORS } from "@/lib/colors";

export default function GraphPage({ params }: { params: { storeId: string } }): JSX.Element {
  return (
    <SiteShell>
      <header className="mb-6 flex items-baseline justify-between">
        <div className="space-y-1">
          <p className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
            /graph/{params.storeId}
          </p>
          <h1 className="text-2xl font-bold tracking-tight">Commerce graph</h1>
        </div>
        <p className="text-sm text-muted-foreground">
          react-force-graph-2d · coming Day 6
        </p>
      </header>

      <div className="grid grid-cols-12 gap-4">
        <aside className="col-span-12 space-y-4 lg:col-span-3">
          <div className="rounded-lg border border-border/60 bg-card/40 p-4">
            <div className="mb-3 font-mono text-xs uppercase tracking-wider text-muted-foreground">
              Node types
            </div>
            <ul className="space-y-2 text-xs">
              {Object.entries(NODE_COLORS).map(([type, color]) => (
                <li key={type} className="flex items-center gap-2">
                  <span
                    className="inline-block h-2.5 w-2.5 rounded-full"
                    style={{ backgroundColor: color }}
                  />
                  <span className="font-mono">{type}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-lg border border-dashed border-border/60 bg-card/40 p-4 text-xs text-muted-foreground">
            Filters (type · min confidence · phase · search · tacit-knowledge category)
          </div>
        </aside>
        <section className="col-span-12 lg:col-span-9">
          <EmptyState
            icon={Network}
            title="Force-directed graph"
            description="Node size ∝ centrality, opacity ∝ confidence, edge thickness ∝ weight, color by type. Click any node for full props + incoming/outgoing edges."
            className="h-[640px]"
          />
        </section>
      </div>
    </SiteShell>
  );
}
