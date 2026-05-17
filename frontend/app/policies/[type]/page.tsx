import { GitBranch } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { SiteShell } from "@/components/site-shell";

export default async function PoliciesPage({
  params,
}: {
  params: Promise<{ type: string }>;
}): Promise<JSX.Element> {
  const { type } = await params;
  return (
    <SiteShell>
      <header className="mb-6 space-y-1">
        <p className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
          /policies/{type}
        </p>
        <h1 className="text-2xl font-bold tracking-tight capitalize">
          {type} decision tree
        </h1>
        <p className="text-sm text-muted-foreground">
          Flowchart from Decision nodes. Each leaf shows per-agent compliance score. Click "Test
          this leaf" to send the edge case to the live simulator.
        </p>
      </header>
      <EmptyState
        icon={GitBranch}
        title="Decision tree flowchart"
        description="Decision Tree visualizer - coming Day 9. Conditional branches, leaf agent-compliance, replayable edge cases."
        className="h-[600px]"
      />
    </SiteShell>
  );
}
