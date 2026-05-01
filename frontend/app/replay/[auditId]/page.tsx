import { Film } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { SiteShell } from "@/components/site-shell";

export default function ReplayPage({
  params,
}: {
  params: { auditId: string };
}): JSX.Element {
  return (
    <SiteShell>
      <header className="mb-6 space-y-1">
        <p className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
          /replay/{params.auditId}
        </p>
        <h1 className="text-2xl font-bold tracking-tight">Replay theater</h1>
        <p className="text-sm text-muted-foreground">
          Scrub the entire audit lifecycle. Top half: state of all 5 views at the timestamp.
          Bottom: scrubbable timeline with tooltips on every event. 4× auto-play.
        </p>
      </header>

      <EmptyState
        icon={Film}
        title="Audit replay"
        description="Replay theater - coming Day 10. Timeline scrubber + synchronized multi-view playback."
        className="h-[520px]"
      />
      <div className="mt-4 rounded-lg border border-dashed border-border/60 bg-card/40 px-4 py-3 font-mono text-xs text-muted-foreground">
        timeline scrubber [|--------|---------|-------------|-------|]
      </div>
    </SiteShell>
  );
}
