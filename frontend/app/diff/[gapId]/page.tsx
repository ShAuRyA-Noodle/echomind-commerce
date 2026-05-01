import { Bot, ScrollText, GitBranch, Wrench } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { SiteShell } from "@/components/site-shell";

export default function DiffPage({ params }: { params: { gapId: string } }): JSX.Element {
  return (
    <SiteShell>
      <header className="mb-6 space-y-1">
        <p className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
          /diff/{params.gapId}
        </p>
        <h1 className="text-2xl font-bold tracking-tight">Gap deep dive</h1>
      </header>

      <div className="grid grid-cols-12 gap-4">
        <section className="col-span-12 lg:col-span-6">
          <EmptyState
            icon={Bot}
            title="Agent says"
            description="Verbatim agent misreading or missing mention. Side by side with merchant truth."
            className="h-[280px]"
          />
        </section>
        <section className="col-span-12 lg:col-span-6">
          <EmptyState
            icon={ScrollText}
            title="Merchant truth"
            description="Stated MerchantTruth + supporting interview snippet + relevant Policy nodes."
            className="h-[280px]"
          />
        </section>
        <section className="col-span-12">
          <EmptyState
            icon={GitBranch}
            title="Reasoning chain"
            description="Each step links to source nodes. Click any step to jump to graph view."
            className="h-[220px]"
          />
        </section>
        <section className="col-span-12 lg:col-span-7">
          <EmptyState
            icon={Wrench}
            title="Revenue impact"
            description="Editable parameters, sensitivity range, calibrated delta prediction."
            className="h-[260px]"
          />
        </section>
        <section className="col-span-12 lg:col-span-5">
          <EmptyState
            icon={Wrench}
            title="Fix suggestion"
            description="Proposed copy + edit + apply. After apply: before/after measured delta."
            className="h-[260px]"
          />
        </section>
      </div>
      <p className="mt-6 font-mono text-xs text-muted-foreground">
        diff view - coming Day 9
      </p>
    </SiteShell>
  );
}
