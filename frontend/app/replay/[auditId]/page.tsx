"use client";

import * as React from "react";
import { Film, Bot, AlertTriangle, Wrench, Loader2, AlertCircle, Clock } from "lucide-react";

import { SiteShell } from "@/components/site-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CalibrationBadge } from "@/components/calibration-badge";
import { request } from "@/lib/api-client";
import type { CalibrationBucket } from "@/lib/colors";
import { cn } from "@/lib/utils";

// ─── API shapes ──────────────────────────────────────────────────────────────

interface AgentEvent {
  event_type: "agent_response";
  id: string;
  agent_model: string;
  response_text: string;
  surfaced_products: string[];
  captured_at: string | null;
  confidence: number | null;
  prompt_text: string;
  intent_class: string;
}

interface GapSummary {
  id: string;
  type: string;
  severity: number;
  calibration_label: string;
  revenue_impact: number;
  affected_products: string[];
}

interface FixEvent {
  id: string;
  gap_id: string;
  fix_type: string;
  applied_at: string | null;
  shopify_resource_id: string | null;
  proposed_text: string;
}

interface TimelineResponse {
  status: string;
  store_id: string;
  events: AgentEvent[];
  gaps: GapSummary[];
  fixes: FixEvent[];
  totals: { agent_responses: number; gaps: number; fixes_applied: number };
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function shortModel(model: string): string {
  if (model.includes("gpt")) return "gpt-oss";
  if (model.includes("llama")) return "llama-3.3";
  if (model.includes("qwen")) return "qwen3";
  if (model.includes("glm")) return "glm-4.5";
  if (model.includes("hermes") || model.includes("nous")) return "hermes";
  return model.split("/").pop()?.slice(0, 14) ?? model;
}

function formatTs(ts: string | null): string {
  if (!ts) return "";
  try {
    return new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  } catch {
    return ts.slice(0, 19).replace("T", " ");
  }
}

const GAP_TYPE_COLOR: Record<string, string> = {
  contradiction: "text-destructive border-destructive/40 bg-destructive/5",
  omission: "text-yellow-400 border-yellow-400/40 bg-yellow-400/5",
  ambiguity: "text-orange-400 border-orange-400/40 bg-orange-400/5",
  hallucination: "text-purple-400 border-purple-400/40 bg-purple-400/5",
  dark_zone: "text-slate-400 border-slate-400/40 bg-slate-400/5",
};

// ─── Sub-components ───────────────────────────────────────────────────────────

function TimelineDot({ color }: { color: string }): React.ReactElement {
  return (
    <div
      className={cn(
        "mt-1 h-3 w-3 shrink-0 rounded-full border-2",
        color,
      )}
    />
  );
}

function ScrubberBar({ events, gaps, fixes }: { events: number; gaps: number; fixes: number }): React.ReactElement {
  const total = events + gaps + fixes;
  const ePct = total ? Math.round((events / total) * 100) : 50;
  const gPct = total ? Math.round((gaps / total) * 100) : 30;
  const fPct = total ? 100 - ePct - gPct : 20;

  return (
    <div className="mb-6 space-y-2">
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span className="font-mono">timeline scrubber</span>
        <span className="font-mono">{total} events</span>
      </div>
      <div className="flex h-3 w-full overflow-hidden rounded-full bg-muted">
        <div
          className="h-full bg-blue-500/70 transition-all"
          style={{ width: `${ePct}%` }}
          title={`${events} agent responses`}
        />
        <div
          className="h-full bg-destructive/70 transition-all"
          style={{ width: `${gPct}%` }}
          title={`${gaps} gaps`}
        />
        <div
          className="h-full bg-emerald-500/70 transition-all"
          style={{ width: `${fPct}%` }}
          title={`${fixes} fixes`}
        />
      </div>
      <div className="flex gap-4 text-[10px] text-muted-foreground">
        <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-blue-500/70 inline-block" />{events} agent responses</span>
        <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-destructive/70 inline-block" />{gaps} gaps</span>
        <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-emerald-500/70 inline-block" />{fixes} fixes applied</span>
      </div>
    </div>
  );
}

// Group agent events by prompt_text for cleaner display
function groupByPrompt(events: AgentEvent[]): Map<string, AgentEvent[]> {
  const map = new Map<string, AgentEvent[]>();
  for (const e of events) {
    const key = e.prompt_text || e.id;
    if (!map.has(key)) map.set(key, []);
    map.get(key)!.push(e);
  }
  return map;
}

// ─── Main component ───────────────────────────────────────────────────────────

export default function ReplayPage({
  params,
}: {
  params: Promise<{ auditId: string }>;
}): React.ReactElement {
  const { auditId } = React.use(params);

  const [data, setData] = React.useState<TimelineResponse | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await request<TimelineResponse>({
          path: `/api/audit/${auditId}/timeline`,
        });
        if (!cancelled) setData(res);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [auditId]);

  const promptGroups = data ? groupByPrompt(data.events) : new Map();
  const totals = data?.totals ?? { agent_responses: 0, gaps: 0, fixes_applied: 0 };

  return (
    <SiteShell>
      <header className="mb-4 space-y-1">
        <p className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
          /replay/{auditId}
        </p>
        <h1 className="flex items-center gap-3 text-2xl font-bold tracking-tight">
          <Film className="h-6 w-6 text-muted-foreground" aria-hidden />
          Replay theater
        </h1>
        <p className="text-sm text-muted-foreground">
          Full audit lifecycle — swarm responses, gap detections, and applied fixes in chronological order.
        </p>
      </header>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading timeline from Neo4j…
        </div>
      )}

      {error && (
        <div className="mb-4 flex items-start gap-2 rounded-md border border-destructive/40 bg-destructive/5 p-3 text-sm text-destructive">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      {!loading && data && (
        <>
          <ScrubberBar
            events={totals.agent_responses}
            gaps={totals.gaps}
            fixes={totals.fixes_applied}
          />

          {totals.agent_responses === 0 && totals.gaps === 0 && (
            <div className="rounded-lg border border-dashed border-border/60 bg-card/40 px-6 py-12 text-center">
              <Film className="mx-auto mb-3 h-8 w-8 text-muted-foreground/40" />
              <p className="text-sm font-medium">No events recorded yet</p>
              <p className="mt-1 text-xs text-muted-foreground">
                Run an interview, then a swarm simulation to populate the timeline.
              </p>
            </div>
          )}

          <div className="space-y-6">
            {/* Swarm responses */}
            {promptGroups.size > 0 && (
              <section>
                <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                  <Bot className="h-4 w-4" />
                  Swarm responses ({totals.agent_responses})
                </h2>
                <div className="space-y-4">
                  {Array.from(promptGroups.entries()).map(([prompt, events]) => (
                    <Card key={prompt} className="border-border/60">
                      <CardHeader className="pb-2">
                        <div className="flex items-start gap-3">
                          <TimelineDot color="border-blue-500 bg-blue-500/20" />
                          <div className="min-w-0">
                            <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                              buyer prompt · {events[0]?.intent_class || "unknown intent"}
                            </p>
                            <p className="mt-0.5 text-sm font-medium leading-snug">
                              {prompt.slice(0, 160) || "(no prompt text)"}
                            </p>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2 pl-6">
                          {events.map((e) => (
                            <div
                              key={e.id}
                              className="rounded-md border border-border/40 bg-muted/20 p-3 text-sm"
                            >
                              <div className="mb-1 flex items-center justify-between gap-2">
                                <span className="font-mono text-[10px] uppercase tracking-wider text-blue-400">
                                  {shortModel(e.agent_model)}
                                </span>
                                {e.captured_at && (
                                  <span className="flex items-center gap-1 font-mono text-[10px] text-muted-foreground">
                                    <Clock className="h-3 w-3" />
                                    {formatTs(e.captured_at)}
                                  </span>
                                )}
                              </div>
                              <p className="leading-snug text-muted-foreground">
                                {(e.response_text || "(no response)").slice(0, 300)}
                              </p>
                              {e.surfaced_products.length > 0 && (
                                <div className="mt-1.5 flex flex-wrap gap-1">
                                  {e.surfaced_products.slice(0, 4).map((p, i) => (
                                    <span
                                      key={i}
                                      className="rounded-sm border border-border/40 bg-muted/50 px-1.5 py-0.5 font-mono text-[10px]"
                                    >
                                      {p}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </section>
            )}

            {/* Gaps detected */}
            {data.gaps.length > 0 && (
              <section>
                <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                  <AlertTriangle className="h-4 w-4" />
                  Gaps detected ({data.gaps.length})
                </h2>
                <div className="space-y-2">
                  {data.gaps.map((g) => (
                    <div key={g.id} className="flex items-start gap-3">
                      <TimelineDot color="border-destructive bg-destructive/20" />
                      <div
                        className={cn(
                          "flex-1 rounded-md border p-3 text-sm",
                          GAP_TYPE_COLOR[g.type] ?? "text-foreground border-border/40 bg-muted/20",
                        )}
                      >
                        <div className="mb-1 flex items-center gap-2">
                          <span className="font-mono text-[10px] uppercase tracking-wider">
                            {g.type}
                          </span>
                          <CalibrationBadge
                            bucket={(g.calibration_label as CalibrationBucket) ?? "uncertain"}
                            score={g.severity}
                          />
                          <span className="ml-auto font-mono text-[10px]">
                            severity {Math.round(g.severity * 100)}%
                          </span>
                        </div>
                        <p className="font-mono text-[10px] text-muted-foreground">
                          {g.id} · {g.affected_products.length} product(s)
                        </p>
                        {g.revenue_impact > 0 && (
                          <p className="mt-0.5 font-mono text-[10px]">
                            ${g.revenue_impact.toFixed(2)}/mo at risk
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Fixes applied */}
            {data.fixes.length > 0 && (
              <section>
                <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                  <Wrench className="h-4 w-4" />
                  Fixes applied ({data.fixes.length})
                </h2>
                <div className="space-y-2">
                  {data.fixes.map((f) => (
                    <div key={f.id} className="flex items-start gap-3">
                      <TimelineDot color="border-emerald-500 bg-emerald-500/20" />
                      <div className="flex-1 rounded-md border border-emerald-500/30 bg-emerald-500/5 p-3 text-sm">
                        <div className="mb-1 flex items-center justify-between">
                          <span className="font-mono text-[10px] uppercase tracking-wider text-emerald-400">
                            {f.fix_type}
                          </span>
                          {f.applied_at && (
                            <span className="flex items-center gap-1 font-mono text-[10px] text-muted-foreground">
                              <Clock className="h-3 w-3" />
                              {formatTs(f.applied_at)}
                            </span>
                          )}
                        </div>
                        {f.shopify_resource_id && (
                          <p className="font-mono text-[10px] text-muted-foreground">
                            → {f.shopify_resource_id}
                          </p>
                        )}
                        {f.proposed_text && (
                          <p className="mt-1 text-xs text-muted-foreground">
                            {f.proposed_text.slice(0, 150)}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>
        </>
      )}
    </SiteShell>
  );
}
