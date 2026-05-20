"use client";

import * as React from "react";
import { Bot, Loader2, ScrollText, Wrench, ArrowLeftRight, AlertCircle } from "lucide-react";

import { CalibrationBadge } from "@/components/calibration-badge";
import { ReasoningTrace, type ReasoningTraceData } from "@/components/reasoning-trace";
import { SiteShell } from "@/components/site-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { CalibrationBucket } from "@/lib/colors";
import { request } from "@/lib/api-client";

// ─── API shapes ──────────────────────────────────────────────────────────────

interface ApiProduct {
  product_id: string;
  title: string;
  shopify_gid: string | null;
  description: string;
}

interface ApiTruth {
  id: string;
  statement: string;
  tacit_category: string | null;
  tacit_level: string | null;
  confidence: number;
  product_id: string | null;
}

interface ApiAgentRep {
  id: string;
  agent_model: string;
  response_text: string;
  confidence: number | null;
  product_id: string | null;
}

interface ApiFixSuggestion {
  id: string | null;
  fix_type: string;
  proposed_text: string;
  applied: boolean;
  applied_at: string | null;
  predicted_delta_low: number | null;
  predicted_delta_high: number | null;
  voice_match_notes: string | null;
}

interface ApiGapDetail {
  status: string;
  gap: {
    id: string;
    type: string;
    severity: number;
    revenue_impact_usd_monthly: number;
    calibration_label: string;
    uncertainty_type: string | null;
    reasoning_chain: string;
    affected_products: ApiProduct[];
  };
  merchant_truths: ApiTruth[];
  agent_representations: ApiAgentRep[];
  fix_suggestion: ApiFixSuggestion | null;
}

// ─── Revenue model ───────────────────────────────────────────────────────────

interface RevenueParams {
  monthly_agent_traffic: number;
  baseline_aov: number;
  baseline_conversion: number;
  surface_loss_rate: number;
  severity: number;
}

const DEFAULTS: RevenueParams = {
  monthly_agent_traffic: 100,
  baseline_aov: 35,
  baseline_conversion: 0.028,
  surface_loss_rate: 0.75,
  severity: 0.83,
};

function revenueAtRisk(p: RevenueParams): { low: number; mid: number; high: number } {
  const base =
    p.severity * p.surface_loss_rate * p.monthly_agent_traffic * p.baseline_aov * p.baseline_conversion;
  return { low: base * 0.7, mid: base, high: base * 1.3 };
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function shortModel(model: string): string {
  if (model.includes("gpt")) return "gpt-oss-120b";
  if (model.includes("llama")) return "llama-3.3-70b";
  if (model.includes("qwen")) return "qwen3-80b";
  if (model.includes("glm")) return "glm-4.5-air";
  if (model.includes("hermes") || model.includes("nous")) return "hermes-405b";
  return model.split("/").pop() ?? model;
}

function buildTrace(data: ApiGapDetail): ReasoningTraceData {
  const { gap, merchant_truths, agent_representations } = data;
  const calibration = (gap.calibration_label as CalibrationBucket) ?? "uncertain";
  const steps = [];

  if (merchant_truths.length > 0) {
    const t = merchant_truths[0];
    steps.push({
      step: 1,
      claim: `Merchant truth (${t.tacit_category ?? "positioning"}): "${t.statement}"`,
      source_node_ids: [t.id],
      confidence: t.confidence ?? 0.85,
    });
  }

  const misrep = agent_representations.slice(0, 3);
  if (misrep.length > 0) {
    steps.push({
      step: steps.length + 1,
      claim: `${misrep.length} of ${agent_representations.length} swarm agents responded: ${misrep
        .map((a) => `[${shortModel(a.agent_model)}] "${(a.response_text ?? "").slice(0, 80)}…"`)
        .join("; ")}`,
      source_node_ids: misrep.map((a) => a.id),
      confidence: 0.88,
    });
  }

  if (gap.reasoning_chain) {
    steps.push({
      step: steps.length + 1,
      claim: gap.reasoning_chain.slice(0, 300),
      source_node_ids: gap.affected_products.map((p) => p.product_id),
      confidence: gap.severity,
    });
  } else {
    steps.push({
      step: steps.length + 1,
      claim: `Gap type: ${gap.type}. Severity ${Math.round(gap.severity * 100)}%. ${
        gap.affected_products.length
      } product(s) affected.`,
      source_node_ids: gap.affected_products.map((p) => p.product_id),
      confidence: gap.severity,
    });
  }

  const knowledgeSources = [
    ...merchant_truths.map((t) => ({ node_id: t.id, type: "MerchantTruth", relevance: t.confidence ?? 0.8 })),
    ...agent_representations.slice(0, 5).map((a) => ({ node_id: a.id, type: "AgentRepresentation", relevance: 0.74 })),
    ...gap.affected_products.map((p) => ({ node_id: p.product_id, type: "Product", relevance: 0.91 })),
  ];

  const contradictions =
    gap.type === "contradiction" && merchant_truths.length > 0 && agent_representations.length > 0
      ? [
          {
            between: [merchant_truths[0].id, agent_representations[0].id],
            resolution: "Trust merchant positioning; agent anchored on generic category stereotype.",
          },
        ]
      : [];

  return {
    answer: gap.reasoning_chain || `${gap.type} gap detected across ${gap.affected_products.length} product(s).`,
    reasoning_chain: steps,
    knowledge_sources_used: knowledgeSources,
    contradictions_resolved: contradictions,
    confidence: gap.severity,
    calibration,
    uncertainty_type: (gap.uncertainty_type as ReasoningTraceData["uncertainty_type"]) ?? null,
  };
}

// ─── Apply result shape ───────────────────────────────────────────────────────

interface ApplyResult {
  applied: boolean;
  shopify_resource_id?: string;
  error?: string;
}

interface RetestDelta {
  before_surface_rate: number;
  after_surface_rate: number;
  delta_pp: number;
  in_predicted_range: boolean;
  n_calls_before: number;
  n_calls_after: number;
}

interface RetestResult {
  status: string;
  fix_id?: string;
  gap_id?: string;
  delta?: RetestDelta;
  n_buyer_prompts?: number;
  n_after_reps?: number;
  detail?: string;
  error?: string;
}

// ─── Component ───────────────────────────────────────────────────────────────

export default function DiffPage({ params }: { params: Promise<{ gapId: string }> }): React.ReactElement {
  const { gapId } = React.use(params);

  const [data, setData] = React.useState<ApiGapDetail | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [fetchError, setFetchError] = React.useState<string | null>(null);

  const [params_, setParams_] = React.useState<RevenueParams>(DEFAULTS);
  const [proposed, setProposed] = React.useState<string>("");
  const [applying, setApplying] = React.useState(false);
  const [applyResult, setApplyResult] = React.useState<ApplyResult | null>(null);
  const [retesting, setRetesting] = React.useState(false);
  const [retestResult, setRetestResult] = React.useState<RetestResult | null>(null);

  // Fetch gap detail from live Neo4j on mount
  React.useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await request<ApiGapDetail>({
          path: `/api/diagnose/_/gap/${gapId}`,
        });
        if (cancelled) return;
        if (res.status === "not_found") {
          setFetchError("Gap not found in graph - run /api/diagnose/run first.");
        } else {
          setData(res);
          // Seed revenue params from gap severity
          setParams_((p) => ({ ...p, severity: res.gap.severity ?? p.severity }));
          // Pre-populate fix textarea
          if (res.fix_suggestion?.proposed_text) {
            setProposed(res.fix_suggestion.proposed_text);
          } else if (res.gap.affected_products[0]?.description) {
            setProposed(res.gap.affected_products[0].description);
          }
        }
      } catch (e) {
        if (!cancelled) setFetchError(e instanceof Error ? e.message : String(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [gapId]);

  async function applyFix(): Promise<void> {
    if (!data || applying) return;
    setApplying(true);
    setApplyResult(null);
    try {
      const fix = data.fix_suggestion;
      const firstProduct = data.gap.affected_products[0];
      const body = {
        fix: {
          id: fix?.id ?? `fix_${gapId}`,
          gap_id: gapId,
          fix_type: fix?.fix_type ?? "copy_rewrite",
          proposed_text: proposed,
          applied: false,
        },
        target_product_gid: firstProduct?.shopify_gid ?? null,
      };
      const res = await request<{ applied: boolean; shopify_resource_id?: string }>({
        method: "POST",
        path: "/api/fix/apply",
        body,
      });
      setApplyResult({ applied: res.applied, shopify_resource_id: res.shopify_resource_id });
    } catch (e) {
      setApplyResult({ applied: false, error: e instanceof Error ? e.message : String(e) });
    } finally {
      setApplying(false);
    }
  }

  async function retestFix(): Promise<void> {
    if (!data || retesting) return;
    const fixId = data.fix_suggestion?.id ?? applyResult?.shopify_resource_id ?? `fix_${gapId}`;
    setRetesting(true);
    setRetestResult(null);
    try {
      const res = await request<RetestResult>({
        method: "POST",
        path: `/api/fix/retest/${encodeURIComponent(fixId)}`,
        body: { demo_mode: true },
      });
      setRetestResult(res);
    } catch (e) {
      setRetestResult({
        status: "error",
        error: e instanceof Error ? e.message : String(e),
      });
    } finally {
      setRetesting(false);
    }
  }

  function jumpToNode(nodeId: string): void {
    if (typeof window !== "undefined") {
      window.open(`/graph/_?focus=${encodeURIComponent(nodeId)}`, "_blank");
    }
  }

  const range = revenueAtRisk(params_);
  const trace = data ? buildTrace(data) : null;
  const calibration: CalibrationBucket = (data?.gap.calibration_label as CalibrationBucket) ?? "uncertain";
  const alreadyApplied = applyResult?.applied || data?.fix_suggestion?.applied;

  return (
    <SiteShell>
      <header className="mb-4 space-y-1">
        <p className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
          /diff/{gapId}
        </p>
        <h1 className="flex items-center gap-3 text-2xl font-bold tracking-tight">
          Gap deep dive
          {trace && <CalibrationBadge bucket={calibration} score={trace.confidence} />}
        </h1>
      </header>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading live gap data from Neo4j…
        </div>
      )}

      {fetchError && (
        <div className="mb-4 flex items-start gap-2 rounded-md border border-destructive/40 bg-destructive/5 p-3 text-sm text-destructive">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{fetchError}</span>
        </div>
      )}

      {!loading && data && (
        <div className="grid grid-cols-12 gap-4">
          {/* Agent says */}
          <Card className="col-span-12 border-border/60 lg:col-span-6">
            <CardHeader className="flex flex-row items-center gap-2 space-y-0 pb-2">
              <Bot className="h-4 w-4 text-muted-foreground" />
              <CardTitle className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                Agent says
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              {data.agent_representations.length === 0 ? (
                <p className="text-xs text-muted-foreground">No agent responses recorded yet - run a swarm simulation.</p>
              ) : (
                data.agent_representations.slice(0, 4).map((a) => (
                  <div
                    key={a.id}
                    className="rounded-md border border-destructive/30 bg-destructive/5 p-3"
                  >
                    <p className="mb-1 font-mono text-[10px] uppercase tracking-wider text-destructive">
                      {shortModel(a.agent_model)}
                    </p>
                    <p className="leading-snug">{(a.response_text ?? "").slice(0, 200)}</p>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          {/* Merchant truth */}
          <Card className="col-span-12 border-border/60 lg:col-span-6">
            <CardHeader className="flex flex-row items-center gap-2 space-y-0 pb-2">
              <ScrollText className="h-4 w-4 text-muted-foreground" />
              <CardTitle className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                Merchant truth
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              {data.merchant_truths.length === 0 ? (
                <p className="text-xs text-muted-foreground">No merchant truths extracted yet - run an interview first.</p>
              ) : (
                data.merchant_truths.slice(0, 3).map((t) => (
                  <div key={t.id} className="rounded-md border border-primary/30 bg-primary/5 p-3">
                    <p className="mb-1 font-mono text-[10px] uppercase tracking-wider text-primary">
                      MerchantTruth
                      {t.tacit_category ? ` · ${t.tacit_category}` : ""}
                      {t.tacit_level ? ` · ${t.tacit_level}` : ""}
                    </p>
                    <p className="leading-snug">{t.statement}</p>
                  </div>
                ))
              )}
              {data.gap.affected_products[0]?.description && (
                <div className="rounded-md border border-border/40 bg-muted/20 p-3">
                  <p className="mb-1 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                    Current product copy
                  </p>
                  <p className="leading-snug text-muted-foreground">
                    {data.gap.affected_products[0].description.slice(0, 300)}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Reasoning chain */}
          <Card className="col-span-12 border-border/60">
            <CardHeader className="flex flex-row items-center gap-2 space-y-0 pb-2">
              <ArrowLeftRight className="h-4 w-4 text-muted-foreground" />
              <CardTitle className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                Reasoning chain
              </CardTitle>
            </CardHeader>
            <CardContent>
              {trace && (
                <ReasoningTrace trace={trace} onSourceClick={jumpToNode} stepIntervalMs={750} />
              )}
            </CardContent>
          </Card>

          {/* Revenue impact */}
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
                  low ${range.low.toFixed(2)} · mid ${range.mid.toFixed(2)} · high $
                  {range.high.toFixed(2)}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Fix suggestion */}
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
                placeholder="Type your proposed copy fix here, or generate one via /api/fix/generate…"
                className="w-full rounded-md border border-border/60 bg-background p-2 text-sm leading-snug"
              />
              <div className="flex items-center justify-between">
                <p className="text-xs text-muted-foreground">
                  {data.fix_suggestion?.predicted_delta_low != null
                    ? `Predicted delta: +${Math.round(data.fix_suggestion.predicted_delta_low * 100)} to +${Math.round((data.fix_suggestion.predicted_delta_high ?? 0) * 100)} pp surface rate`
                    : "Edit copy above, then apply to Shopify"}
                </p>
                <Button
                  onClick={applyFix}
                  size="sm"
                  disabled={Boolean(alreadyApplied) || applying || !proposed.trim()}
                >
                  {applying ? (
                    <><Loader2 className="mr-1 h-3 w-3 animate-spin" />Applying…</>
                  ) : alreadyApplied ? (
                    "Applied ✓"
                  ) : (
                    "Apply to Shopify"
                  )}
                </Button>
              </div>

              {applyResult?.applied && (
                <div className="rounded-md border border-emerald-500/40 bg-emerald-500/5 p-3 text-xs">
                  <p className="mb-1 font-mono text-emerald-300">
                    Applied to Shopify
                    {applyResult.shopify_resource_id
                      ? ` · resource: ${applyResult.shopify_resource_id}`
                      : ""}
                  </p>
                  <p className="text-muted-foreground">
                    Fix persisted to Neo4j as FixSuggestion node. Click <span className="font-mono">Re-test</span> below
                    to rerun the swarm and measure observed_delta.
                  </p>
                </div>
              )}

              {applyResult?.error && (
                <div className="rounded-md border border-destructive/40 bg-destructive/5 p-3 text-xs text-destructive">
                  <p className="mb-1 font-mono">Apply error</p>
                  <p>{applyResult.error}</p>
                </div>
              )}

              {data.fix_suggestion?.voice_match_notes && (
                <p className="text-xs text-muted-foreground">
                  Voice: {data.fix_suggestion.voice_match_notes}
                </p>
              )}

              {/* Re-test row */}
              <div className="border-t border-border/40 pt-3">
                <div className="flex items-center justify-between">
                  <p className="text-xs text-muted-foreground">
                    Measure observed delta - rerun swarm against historical buyer prompts.
                  </p>
                  <Button
                    onClick={retestFix}
                    size="sm"
                    variant="outline"
                    disabled={retesting}
                  >
                    {retesting ? (
                      <><Loader2 className="mr-1 h-3 w-3 animate-spin" />Re-testing…</>
                    ) : retestResult?.delta ? (
                      "Re-test again"
                    ) : (
                      "Re-test"
                    )}
                  </Button>
                </div>

                {retestResult?.delta && (
                  <div className="mt-3 rounded-md border border-blue-500/40 bg-blue-500/5 p-3 text-xs">
                    <div className="mb-2 flex items-center justify-between">
                      <p className="font-mono text-blue-300">
                        observed_delta: {retestResult.delta.delta_pp >= 0 ? "+" : ""}
                        {retestResult.delta.delta_pp.toFixed(1)} pp surface rate
                      </p>
                      <span
                        className={`rounded-sm border px-1.5 py-0.5 font-mono text-[10px] ${
                          retestResult.delta.in_predicted_range
                            ? "border-emerald-500/40 text-emerald-400"
                            : "border-yellow-500/40 text-yellow-400"
                        }`}
                      >
                        {retestResult.delta.in_predicted_range ? "in predicted range" : "outside predicted range"}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 font-mono">
                      <span>
                        before {Math.round(retestResult.delta.before_surface_rate * 100)}%
                      </span>
                      <span className="text-muted-foreground">→</span>
                      <span>
                        after {Math.round(retestResult.delta.after_surface_rate * 100)}%
                      </span>
                      <span className="ml-auto text-muted-foreground">
                        {retestResult.delta.n_calls_before} before · {retestResult.delta.n_calls_after} after
                      </span>
                    </div>
                  </div>
                )}

                {retestResult?.status && retestResult.status !== "ok" && !retestResult.delta && (
                  <div className="mt-3 rounded-md border border-yellow-500/40 bg-yellow-500/5 p-3 text-xs text-yellow-300">
                    <p className="font-mono">{retestResult.status}</p>
                    {retestResult.detail && <p className="mt-1 text-muted-foreground">{retestResult.detail}</p>}
                    {retestResult.error && <p className="mt-1 text-destructive">{retestResult.error}</p>}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </SiteShell>
  );
}
