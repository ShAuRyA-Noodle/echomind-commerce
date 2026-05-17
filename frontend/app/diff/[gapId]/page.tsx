"use client";

import * as React from "react";
import { Bot, ScrollText, Wrench, ArrowLeftRight } from "lucide-react";

import { CalibrationBadge } from "@/components/calibration-badge";
import { ReasoningTrace, type ReasoningTraceData } from "@/components/reasoning-trace";
import { SiteShell } from "@/components/site-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { CalibrationBucket } from "@/lib/colors";

/**
 * Sample reasoning trace mirroring the demo Yirgacheffe contradiction.
 * Hooked to the cinematic ReasoningTrace animation. When the diagnose
 * pipeline ships per-gap reasoning persistence (Firestore v2), this page
 * fetches the live trace from `/api/diagnose/{run_id}/gap/{gap_id}`.
 */
const SAMPLE_TRACE: ReasoningTraceData = {
  answer:
    "Three of four agents represent your Yirgacheffe as 'fruity, acidic.' Your interview said 'chocolate-forward.' Likely cause: the product description omits chocolate, low-acidity, and Bourbon-varietal cues.",
  reasoning_chain: [
    {
      step: 1,
      claim:
        "Merchant truth captured in Phase 2 (Product Truths) labels Yirgacheffe as chocolate-forward, low-acidity, Bourbon varietal.",
      source_node_ids: ["truth_yirg_chocolate_forward"],
      confidence: 0.92,
    },
    {
      step: 2,
      claim:
        "Three swarm agents (gpt_oss, llama, qwen) describe the product as fruity / acidic / floral when asked for a chocolatey single-origin.",
      source_node_ids: [
        "agent_repr_gpt_oss_yirg_001",
        "agent_repr_llama_yirg_001",
        "agent_repr_qwen_yirg_001",
      ],
      confidence: 0.88,
    },
    {
      step: 3,
      claim:
        "Catalog descriptionHtml for the same product contains zero occurrences of 'chocolate', 'low acidity', or 'Bourbon'.",
      source_node_ids: ["prod_yirgacheffe_250g"],
      confidence: 0.99,
    },
    {
      step: 4,
      claim:
        "GLM-4.5 is the lone outlier and surfaced the product without misrepresentation; classification: contradiction (not ambiguity).",
      source_node_ids: ["agent_repr_glm_yirg_001"],
      confidence: 0.78,
    },
  ],
  knowledge_sources_used: [
    { node_id: "truth_yirg_chocolate_forward", type: "MerchantTruth", relevance: 0.95 },
    { node_id: "prod_yirgacheffe_250g", type: "Product", relevance: 0.91 },
    { node_id: "agent_repr_gpt_oss_yirg_001", type: "AgentRepresentation", relevance: 0.74 },
    { node_id: "agent_repr_llama_yirg_001", type: "AgentRepresentation", relevance: 0.74 },
    { node_id: "agent_repr_qwen_yirg_001", type: "AgentRepresentation", relevance: 0.74 },
  ],
  contradictions_resolved: [
    {
      between: ["truth_yirg_chocolate_forward", "agent_repr_gpt_oss_yirg_001"],
      resolution:
        "Trust merchant; agent description omits 'chocolate' and is anchored on the public-Yirgacheffe stereotype.",
    },
  ],
  confidence: 0.83,
  calibration: "confident",
  uncertainty_type: null,
};

interface RevenueParams {
  monthly_agent_traffic: number;
  baseline_aov: number;
  baseline_conversion: number;
  surface_loss_rate: number;
  severity: number;
}

const DEFAULTS: RevenueParams = {
  monthly_agent_traffic: 100,
  baseline_aov: 18,
  baseline_conversion: 0.025,
  surface_loss_rate: 0.75,
  severity: 0.83,
};

function revenueAtRisk(p: RevenueParams): { low: number; mid: number; high: number } {
  const base = p.severity * p.surface_loss_rate * p.monthly_agent_traffic * p.baseline_aov * p.baseline_conversion;
  return { low: base * 0.7, mid: base, high: base * 1.3 };
}

export default function DiffPage({ params }: { params: Promise<{ gapId: string }> }): React.ReactElement {
  const { gapId } = React.use(params);
  const [trace] = React.useState<ReasoningTraceData>(SAMPLE_TRACE);
  const [params_, setParams_] = React.useState<RevenueParams>(DEFAULTS);
  const [proposed, setProposed] = React.useState<string>(
    "Yirgacheffe (Bourbon varietal) - chocolate-forward, low-acidity, syrupy body. Notes of dark cocoa and brown sugar with a clean, lingering finish. Best for V60 and chemex; not recommended for cold brew."
  );
  const [applied, setApplied] = React.useState<{ before: number; after: number } | null>(null);

  const range = revenueAtRisk(params_);

  function applyFix(): void {
    // In production: POST /api/fix/apply with the hydrated FixSuggestion.
    // For now: simulate the optimistic before/after delta render.
    setApplied({ before: 12, after: 71 });
  }

  function jumpToNode(nodeId: string): void {
    // Lazy: open /graph view in a new tab anchored on the node.
    if (typeof window !== "undefined") {
      window.open(`/graph/_?focus=${encodeURIComponent(nodeId)}`, "_blank");
    }
  }

  const calibration: CalibrationBucket = trace.calibration;

  return (
    <SiteShell>
      <header className="mb-4 space-y-1">
        <p className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
          /diff/{gapId}
        </p>
        <h1 className="flex items-center gap-3 text-2xl font-bold tracking-tight">
          Gap deep dive
          <CalibrationBadge bucket={calibration} score={trace.confidence} />
        </h1>
      </header>

      <div className="grid grid-cols-12 gap-4">
        <Card className="col-span-12 border-border/60 lg:col-span-6">
          <CardHeader className="flex flex-row items-center gap-2 space-y-0 pb-2">
            <Bot className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Agent says
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="rounded-md border border-destructive/30 bg-destructive/5 p-3">
              <p className="mb-1 font-mono text-[10px] uppercase tracking-wider text-destructive">
                gpt-oss-120b:free
              </p>
              <p className="leading-snug">
                "Try the Ethiopia Yirgacheffe - it's a fruity, floral profile with vibrant
                acidity and jasmine notes. Great for filter brews."
              </p>
            </div>
            <div className="rounded-md border border-destructive/30 bg-destructive/5 p-3">
              <p className="mb-1 font-mono text-[10px] uppercase tracking-wider text-destructive">
                llama-3.3-70b:free
              </p>
              <p className="leading-snug">
                "Yirgacheffe leans bright and fruity - lemon, jasmine. If you want something
                chocolatey, look elsewhere on the menu."
              </p>
            </div>
            <div className="rounded-md border border-emerald-500/30 bg-emerald-500/5 p-3">
              <p className="mb-1 font-mono text-[10px] uppercase tracking-wider text-emerald-300">
                glm-4.5-air:free (outlier)
              </p>
              <p className="leading-snug">
                "Yirgacheffe naturals can vary. Their tasting notes mention smooth body but
                are vague on roast - I'd recommend reading the product page before assuming
                fruity."
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="col-span-12 border-border/60 lg:col-span-6">
          <CardHeader className="flex flex-row items-center gap-2 space-y-0 pb-2">
            <ScrollText className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Merchant truth
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="rounded-md border border-primary/30 bg-primary/5 p-3">
              <p className="mb-1 font-mono text-[10px] uppercase tracking-wider text-primary">
                MerchantTruth - phase: product_truths - tacit_level: deeply-tacit
              </p>
              <p className="leading-snug">
                "Our Yirgacheffe is chocolate-forward, not the typical bright/floral Yirg
                profile. We source Bourbon varietal lots and roast slightly past first
                crack to land low-acidity in the cup."
              </p>
            </div>
            <div className="rounded-md border border-border/40 bg-muted/20 p-3">
              <p className="mb-1 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                Product page (current copy)
              </p>
              <p className="leading-snug text-muted-foreground">
                "Fruity floral profile, vibrant acidity, jasmine notes. Tea-like body that
                thins into bergamot on the finish."
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="col-span-12 border-border/60">
          <CardHeader className="flex flex-row items-center gap-2 space-y-0 pb-2">
            <ArrowLeftRight className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Reasoning chain
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ReasoningTrace trace={trace} onSourceClick={jumpToNode} stepIntervalMs={750} />
          </CardContent>
        </Card>

        <Card className="col-span-12 border-border/60 lg:col-span-7">
          <CardHeader className="flex flex-row items-center gap-2 space-y-0 pb-2">
            <Wrench className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Revenue impact
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
              {(
                [
                  ["severity", "severity"],
                  ["surface_loss_rate", "surface loss"],
                  ["monthly_agent_traffic", "monthly agents"],
                  ["baseline_aov", "AOV (USD)"],
                  ["baseline_conversion", "conv rate"],
                ] as Array<[keyof RevenueParams, string]>
              ).map(([k, label]) => (
                <label key={k} className="space-y-1 text-xs">
                  <span className="text-muted-foreground">{label}</span>
                  <input
                    type="number"
                    step={k === "monthly_agent_traffic" ? 10 : 0.01}
                    value={params_[k]}
                    onChange={(e) =>
                      setParams_((p) => ({ ...p, [k]: Number(e.target.value) || 0 }))
                    }
                    className="w-full rounded-md border border-border/60 bg-background px-2 py-1 font-mono text-xs"
                  />
                </label>
              ))}
            </div>
            <div className="rounded-md border border-border/40 bg-muted/20 p-3 text-xs">
              <div className="text-muted-foreground">Monthly $ at risk (range)</div>
              <div className="mt-1 font-mono">
                low ${range.low.toFixed(2)} - mid ${range.mid.toFixed(2)} - high $
                {range.high.toFixed(2)}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="col-span-12 border-border/60 lg:col-span-5">
          <CardHeader className="flex flex-row items-center gap-2 space-y-0 pb-2">
            <Wrench className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Fix suggestion
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <textarea
              value={proposed}
              onChange={(e) => setProposed(e.target.value)}
              rows={6}
              className="w-full rounded-md border border-border/60 bg-background p-2 text-sm leading-snug"
            />
            <div className="flex items-center justify-between">
              <p className="text-xs text-muted-foreground">
                Predicted delta: +40 to +75 pp surface rate (calibration: confident)
              </p>
              <Button onClick={applyFix} size="sm" disabled={Boolean(applied)}>
                {applied ? "Applied" : "Apply to Shopify"}
              </Button>
            </div>
            {applied && (
              <div className="rounded-md border border-emerald-500/40 bg-emerald-500/5 p-3 text-xs">
                <p className="mb-1 font-mono text-emerald-300">
                  before {applied.before}% - after {applied.after}% surface rate (sample data)
                </p>
                <p className="text-muted-foreground">
                  Live re-test runs the same buyer prompts against the same agents and
                  populates observed_delta on the FixSuggestion node.
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </SiteShell>
  );
}
