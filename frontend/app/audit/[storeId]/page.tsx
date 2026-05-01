"use client";

import * as React from "react";
import { Activity, AlertTriangle, Map, Radar } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { GapCard, type GapType } from "@/components/gap-card";
import { SiteShell } from "@/components/site-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiClient } from "@/lib/api-client";
import type { CalibrationBucket } from "@/lib/colors";

interface AuditSummary {
  status: string;
  store_id: string;
  readiness_score: number;
  calibration_mix?: Record<string, number>;
  totals?: {
    products: number;
    merchant_truths: number;
    agent_representations: number;
    gaps: number;
    fixes: number;
  };
  graph?: { nodes?: Record<string, number>; edges?: Record<string, number> };
}

interface ApiGap {
  gap_id: string;
  gap_type: string;
  severity: number;
  calibration_label: string;
  revenue_impact: number;
  affected_products: { product_id: string; title: string }[];
}

const VALID_GAP_TYPES: ReadonlyArray<GapType> = [
  "omission",
  "contradiction",
  "ambiguity",
  "hallucination",
  "dark_zone",
];

const VALID_CAL: ReadonlyArray<CalibrationBucket> = [
  "certain",
  "confident",
  "uncertain",
  "low_confidence",
  "dont_know",
];

function asGapType(t: string): GapType {
  return (VALID_GAP_TYPES as readonly string[]).includes(t)
    ? (t as GapType)
    : "omission";
}

function asCalibration(c: string): CalibrationBucket {
  return (VALID_CAL as readonly string[]).includes(c)
    ? (c as CalibrationBucket)
    : "uncertain";
}

export default function AuditPage({ params }: { params: { storeId: string } }): React.ReactElement {
  const [summary, setSummary] = React.useState<AuditSummary | null>(null);
  const [gaps, setGaps] = React.useState<ApiGap[]>([]);
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [s, g] = await Promise.all([
          apiClient.request<AuditSummary>({ path: `/api/audit/${params.storeId}` }),
          apiClient.request<{ gaps: ApiGap[] }>({ path: `/api/audit/${params.storeId}/gaps` }),
        ]);
        if (cancelled) return;
        setSummary(s);
        setGaps(g.gaps ?? []);
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : String(e));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [params.storeId]);

  const totals = summary?.totals;
  const readiness = summary?.readiness_score;

  return (
    <SiteShell>
      <header className="mb-6 space-y-1">
        <p className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
          /audit/{params.storeId}
        </p>
        <h1 className="text-2xl font-bold tracking-tight">AI Readiness Audit</h1>
        {error && (
          <p className="rounded-md border border-destructive/40 bg-destructive/5 p-2 text-xs text-destructive">
            Backend unreachable: {error}
          </p>
        )}
      </header>

      <section className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">
              AI Readiness Score
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="font-mono text-3xl font-bold">
              {loading ? "..." : readiness ?? "--"}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">
              Merchant truths
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="font-mono text-3xl font-bold">
              {loading ? "..." : totals?.merchant_truths ?? "--"}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">
              Agent representations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="font-mono text-3xl font-bold">
              {loading ? "..." : totals?.agent_representations ?? "--"}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-muted-foreground">
              Gaps detected
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="font-mono text-3xl font-bold">
              {loading ? "..." : totals?.gaps ?? "--"}
            </div>
          </CardContent>
        </Card>
      </section>

      <div className="grid grid-cols-12 gap-4">
        <section className="col-span-12 space-y-3 lg:col-span-8">
          <div className="flex items-center justify-between">
            <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              <AlertTriangle className="h-4 w-4" aria-hidden />
              Ranked gaps
            </h2>
            <span className="font-mono text-xs text-muted-foreground">
              {loading ? "loading..." : `${gaps.length} gaps live from /api/audit`}
            </span>
          </div>
          {gaps.length === 0 && !loading && (
            <EmptyState
              icon={AlertTriangle}
              title="No gaps detected yet"
              description="Run /api/diagnose/run after seeding the catalog and running a swarm pass."
            />
          )}
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            {gaps.map((g) => (
              <GapCard
                key={g.gap_id}
                title={g.affected_products?.[0]?.title || g.gap_id}
                type={asGapType(g.gap_type)}
                severity={g.severity}
                revenueAtRisk={g.revenue_impact}
                calibration={asCalibration(g.calibration_label)}
                affectedProducts={g.affected_products?.length ?? 0}
              />
            ))}
          </div>
        </section>
        <aside className="col-span-12 space-y-4 lg:col-span-4">
          <EmptyState
            icon={Radar}
            title="AI Readiness Radar"
            description="5 axes: catalog clarity, policy completeness, FAQ coverage, trust signals, edge cases."
            className="h-[280px]"
          />
          <EmptyState
            icon={Map}
            title="Coverage heatmap"
            description="Treemap colored green / yellow / red, which categories are well-represented vs dark zones."
            className="h-[260px]"
          />
        </aside>
      </div>
      <div className="mt-6 flex items-center gap-2 text-xs text-muted-foreground">
        <Activity className="h-3.5 w-3.5" aria-hidden />
        <span className="font-mono">live data via /api/audit/{"{storeId}"} + /api/audit/{"{storeId}"}/gaps</span>
      </div>
    </SiteShell>
  );
}
