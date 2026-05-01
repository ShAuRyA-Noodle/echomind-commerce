import { Mic, MessageSquare, Network } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { SiteShell } from "@/components/site-shell";

export default function InterviewPage({ params }: { params: { id: string } }): JSX.Element {
  return (
    <SiteShell>
      <div className="mb-6 flex items-baseline justify-between">
        <div className="space-y-1">
          <p className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
            /interview/{params.id}
          </p>
          <h1 className="text-2xl font-bold tracking-tight">Live interview</h1>
        </div>
        <p className="text-sm text-muted-foreground">
          Phase 1/5 · 00:00 elapsed · coming Day 5
        </p>
      </div>
      <div className="grid grid-cols-12 gap-4">
        <section className="col-span-12 lg:col-span-4">
          <EmptyState
            icon={MessageSquare}
            title="Transcript"
            description="Live transcript pane - interim italic, final solid, extracted-as-node phrases highlighted and clickable."
            className="h-[640px]"
          />
        </section>
        <section className="col-span-12 lg:col-span-5">
          <EmptyState
            icon={Mic}
            title="Current question"
            description="Large-readable question, 5-segment phase indicator, audio controls, voice-activity LED, text fallback."
            className="h-[640px]"
          />
        </section>
        <section className="col-span-12 lg:col-span-3">
          <EmptyState
            icon={Network}
            title="Mini graph"
            description="Force-directed mini view. New nodes pulse in, colored by type. Live counters: nodes / edges / coverage."
            className="h-[640px]"
          />
        </section>
      </div>
    </SiteShell>
  );
}
