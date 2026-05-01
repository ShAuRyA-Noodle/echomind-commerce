import Link from "next/link";
import { ArrowRight, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { SiteShell } from "@/components/site-shell";

export default function LandingPage(): JSX.Element {
  return (
    <SiteShell>
      <section className="flex flex-col items-center justify-center gap-8 py-24 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-card/50 px-3 py-1 text-xs font-medium text-muted-foreground">
          <Sparkles className="h-3.5 w-3.5 text-[var(--node-fix-suggestion)]" aria-hidden />
          Track 5 · AI Representation Optimizer
        </div>
        <h1 className="max-w-3xl text-balance text-5xl font-bold tracking-tight md:text-6xl">
          See exactly what AI agents <span className="text-[var(--node-product)]">say</span> about
          your store - and fix it.
        </h1>
        <p className="max-w-2xl text-balance text-lg text-muted-foreground">
          Echomind Commerce interviews you, builds a calibrated commerce graph, runs four real LLM
          buyer agents against your catalog, and shows you every gap, contradiction, and missing
          fact - ranked by revenue at risk.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-3">
          <Link href="/onboard">
            <Button size="lg">
              Get started
              <ArrowRight className="ml-2 h-4 w-4" aria-hidden />
            </Button>
          </Link>
          <Link href="/audit/demo">
            <Button size="lg" variant="outline">
              View sample audit
            </Button>
          </Link>
        </div>
        <div className="grid w-full max-w-4xl grid-cols-2 gap-3 pt-12 text-left text-sm md:grid-cols-4">
          {[
            { label: "Interview", color: "var(--node-customer-question)" },
            { label: "Audit", color: "var(--node-policy)" },
            { label: "Simulate", color: "var(--node-agent-representation)" },
            { label: "Fix → Re-test", color: "var(--node-fix-suggestion)" },
          ].map((step) => (
            <div
              key={step.label}
              className="rounded-lg border border-border/60 bg-card/40 px-4 py-3"
            >
              <div
                className="mb-2 h-1.5 w-8 rounded-full"
                style={{ backgroundColor: step.color }}
              />
              <div className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
                {step.label}
              </div>
            </div>
          ))}
        </div>
      </section>
    </SiteShell>
  );
}
