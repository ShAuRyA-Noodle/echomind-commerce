"use client";

import * as React from "react";
import { Check, CircleDashed, Loader2, Plug, ShoppingBag, UserCircle } from "lucide-react";

import { SiteShell } from "@/components/site-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { apiClient } from "@/lib/api-client";

interface IngestStatus {
  status: string;
  shop?: string | null;
  currency?: string | null;
  products?: number;
  policies?: number;
  reviews?: number;
  duration_seconds?: number;
}

interface IngestStatsResponse {
  status: string;
  nodes?: Record<string, number>;
  edges?: Record<string, number>;
}

const STEPS: ReadonlyArray<{
  n: number;
  title: string;
  description: string;
  icon: typeof Check;
}> = [
  {
    n: 1,
    title: "Sign in with Google",
    description: "Firebase Auth, one click, no passwords.",
    icon: UserCircle,
  },
  {
    n: 2,
    title: "Connect Shopify (Custom App)",
    description: "Admin API access token from .env. v2 marketplace flow stub also lives here.",
    icon: Plug,
  },
  {
    n: 3,
    title: "Live ingest",
    description:
      "Click Run ingest to crawl products, policies, and reviews live via Admin GraphQL into Neo4j.",
    icon: ShoppingBag,
  },
  {
    n: 4,
    title: "Start the audit",
    description: "20 min Socratic interview + 5 min agent simulation.",
    icon: CircleDashed,
  },
];

export default function OnboardPage(): React.ReactElement {
  const [running, setRunning] = React.useState(false);
  const [result, setResult] = React.useState<IngestStatus | null>(null);
  const [stats, setStats] = React.useState<IngestStatsResponse | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  async function refreshStats(): Promise<void> {
    try {
      const s = await apiClient.request<IngestStatsResponse>({
        path: "/api/onboard/ingest/status",
      });
      setStats(s);
    } catch {
      // Silent: backend may be down. Status block already shows guidance.
    }
  }

  React.useEffect(() => {
    refreshStats();
  }, []);

  async function runIngest(): Promise<void> {
    setRunning(true);
    setError(null);
    setResult(null);
    try {
      const r = await apiClient.request<IngestStatus>({
        method: "POST",
        path: "/api/onboard/ingest/run",
        body: {},
      });
      setResult(r);
      await refreshStats();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setRunning(false);
    }
  }

  return (
    <SiteShell>
      <div className="mx-auto max-w-3xl space-y-8">
        <header className="space-y-2">
          <p className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
            /onboard
          </p>
          <h1 className="text-3xl font-bold tracking-tight">Connect your Shopify store</h1>
          <p className="text-muted-foreground">
            Real Shopify Admin GraphQL crawl into Neo4j. Idempotent, safe to re-run.
          </p>
        </header>

        <ol className="space-y-3">
          {STEPS.map((step) => {
            const Icon = step.icon;
            return (
              <li key={step.n}>
                <Card className="border-border/60">
                  <CardHeader className="flex flex-row items-start gap-4 space-y-0">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-muted">
                      <Icon className="h-5 w-5 text-muted-foreground" aria-hidden />
                    </div>
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs text-muted-foreground">
                          STEP {step.n}
                        </span>
                      </div>
                      <CardTitle className="text-lg">{step.title}</CardTitle>
                      <CardDescription>{step.description}</CardDescription>
                    </div>
                  </CardHeader>
                </Card>
              </li>
            );
          })}
        </ol>

        <Card className="border-border/60">
          <CardHeader>
            <CardTitle className="text-base">Run live ingest</CardTitle>
            <CardDescription>
              Hits POST /api/onboard/ingest/run. Crawls Shopify Admin GraphQL with the configured
              SHOPIFY_ADMIN_ACCESS_TOKEN, writes typed Product, Policy, TrustSignal nodes to Neo4j.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button onClick={runIngest} disabled={running}>
              {running ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden />
                  Crawling Shopify...
                </>
              ) : (
                "Run ingest"
              )}
            </Button>
            {result && (
              <div className="rounded-md border border-border/60 bg-muted/30 p-3 text-sm">
                <p>
                  Shop: <span className="font-mono">{result.shop ?? "n/a"}</span>{" "}
                  Currency: <span className="font-mono">{result.currency ?? "n/a"}</span>
                </p>
                <p className="font-mono text-xs">
                  products: {result.products} · policies: {result.policies} ·{" "}
                  reviews: {result.reviews} · duration: {result.duration_seconds}s
                </p>
              </div>
            )}
            {error && (
              <p className="rounded-md border border-destructive/40 bg-destructive/5 p-2 text-xs text-destructive">
                Ingest failed: {error}
              </p>
            )}
            {stats && (
              <div className="rounded-md border border-dashed border-border/50 p-3 text-xs">
                <p className="mb-1 font-mono text-muted-foreground">Live Neo4j counts</p>
                {stats.nodes && Object.keys(stats.nodes).length > 0 ? (
                  <ul className="space-y-0.5">
                    {Object.entries(stats.nodes).map(([k, v]) => (
                      <li key={k} className="font-mono">
                        {k}: {v}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="font-mono text-muted-foreground">empty graph</p>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </SiteShell>
  );
}
