"use client";

import * as React from "react";
import { GitBranch, Loader2, AlertCircle, ChevronRight } from "lucide-react";

import { SiteShell } from "@/components/site-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { request } from "@/lib/api-client";
import { cn } from "@/lib/utils";

// ─── API shapes ──────────────────────────────────────────────────────────────

interface DecisionNode {
  id: string;
  question: string;
  context: string;
  outcome: string;
  conditions: string[];
  frequency: string;
  confidence: number;
}

interface DecisionsResponse {
  status: string;
  store_id: string;
  decisions: DecisionNode[];
  total: number;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function confidenceColor(c: number): string {
  if (c >= 0.85) return "bg-emerald-500";
  if (c >= 0.65) return "bg-yellow-400";
  return "bg-destructive";
}

function confidenceLabel(c: number): string {
  if (c >= 0.85) return "high";
  if (c >= 0.65) return "medium";
  return "low";
}

// ─── Decision Card ────────────────────────────────────────────────────────────

function DecisionCard({ node, index }: { node: DecisionNode; index: number }): React.ReactElement {
  const [expanded, setExpanded] = React.useState(index < 3);

  return (
    <Card
      className={cn(
        "border-border/60 transition-all",
        expanded ? "bg-card" : "bg-card/60",
      )}
    >
      <CardHeader
        className="cursor-pointer select-none pb-2"
        onClick={() => setExpanded((e) => !e)}
      >
        <div className="flex items-start gap-3">
          <GitBranch className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
          <div className="min-w-0 flex-1">
            <div className="flex items-center justify-between gap-2">
              <p className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                decision · conf {confidenceLabel(node.confidence)} ({Math.round(node.confidence * 100)}%)
              </p>
              <ChevronRight
                className={cn(
                  "h-3.5 w-3.5 shrink-0 text-muted-foreground transition-transform",
                  expanded && "rotate-90",
                )}
              />
            </div>
            <CardTitle className="mt-1 text-sm leading-snug">
              {node.question || "(no question)"}
            </CardTitle>
          </div>
        </div>
        {/* Confidence bar */}
        <div className="ml-7 mt-2 h-1 w-full overflow-hidden rounded-full bg-muted">
          <div
            className={cn("h-full transition-all", confidenceColor(node.confidence))}
            style={{ width: `${Math.round(node.confidence * 100)}%` }}
          />
        </div>
      </CardHeader>

      {expanded && (
        <CardContent className="space-y-3 pl-10 text-sm">
          {node.context && (
            <div>
              <p className="mb-0.5 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                Context
              </p>
              <p className="leading-snug text-muted-foreground">{node.context}</p>
            </div>
          )}

          {node.outcome && (
            <div className="rounded-md border border-primary/30 bg-primary/5 p-2.5">
              <p className="mb-0.5 font-mono text-[10px] uppercase tracking-wider text-primary">
                Outcome
              </p>
              <p className="leading-snug">{node.outcome}</p>
            </div>
          )}

          {node.conditions.length > 0 && (
            <div>
              <p className="mb-1 font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                Conditions
              </p>
              <div className="flex flex-wrap gap-1">
                {node.conditions.map((c, i) => (
                  <span
                    key={i}
                    className="rounded-sm border border-border/60 bg-muted/50 px-1.5 py-0.5 font-mono text-[10px]"
                  >
                    {c}
                  </span>
                ))}
              </div>
            </div>
          )}

          {node.frequency && (
            <p className="font-mono text-[10px] text-muted-foreground">
              frequency: {node.frequency}
            </p>
          )}

          <p className="font-mono text-[10px] text-muted-foreground opacity-50">
            id: {node.id}
          </p>
        </CardContent>
      )}
    </Card>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

export default function PoliciesPage({
  params,
}: {
  params: Promise<{ type: string }>;
}): React.ReactElement {
  const { type } = React.use(params);

  const [data, setData] = React.useState<DecisionsResponse | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const query = type && type !== "all" ? { type } : undefined;
        const res = await request<DecisionsResponse>({
          path: "/api/audit/demo/decisions",
          query,
        });
        if (!cancelled) setData(res);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [type]);

  const filtered = data?.decisions ?? [];
  const displayType = type.replace(/-/g, " ");

  return (
    <SiteShell>
      <header className="mb-6 space-y-1">
        <p className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
          /policies/{type}
        </p>
        <h1 className="flex items-center gap-3 text-2xl font-bold tracking-tight capitalize">
          <GitBranch className="h-6 w-6 text-muted-foreground" aria-hidden />
          {displayType} decision tree
        </h1>
        <p className="text-sm text-muted-foreground">
          Merchant decision nodes extracted from the Socratic interview. Each node shows
          the question, context, outcome, and confidence - live from Neo4j.
        </p>
      </header>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading decision nodes from Neo4j…
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
          <div className="mb-4 flex items-center justify-between">
            <span className="font-mono text-xs text-muted-foreground">
              {filtered.length} of {data.total} decision nodes
              {type !== "all" && ` matching "${displayType}"`}
            </span>
            <span className="font-mono text-xs text-muted-foreground">
              live · /api/audit/demo/decisions
            </span>
          </div>

          {filtered.length === 0 ? (
            <div className="rounded-lg border border-dashed border-border/60 bg-card/40 px-6 py-12 text-center">
              <GitBranch className="mx-auto mb-3 h-8 w-8 text-muted-foreground/40" />
              <p className="text-sm font-medium">
                {data.total === 0
                  ? "No decision nodes yet"
                  : `No decisions match "${displayType}"`}
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                {data.total === 0
                  ? "Run a Socratic interview to extract merchant decisions into the graph."
                  : "Try /policies/all to see all decisions."}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filtered.map((node, i) => (
                <DecisionCard key={node.id} node={node} index={i} />
              ))}
            </div>
          )}
        </>
      )}
    </SiteShell>
  );
}
