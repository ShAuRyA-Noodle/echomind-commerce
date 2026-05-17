"use client";

import * as React from "react";
import { Bot, Play, Activity } from "lucide-react";

import { SiteShell } from "@/components/site-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useSimulateSocket } from "@/lib/hooks/use-simulate-socket";

const SLOT_LABEL: Record<string, string> = {
  gpt_oss: "GPT-OSS 120B",
  llama: "Llama 3.3 70B",
  qwen: "Qwen3 80B (MoE)",
  glm: "GLM-4.5 Air",
};

const SLOT_MODEL: Record<string, string> = {
  gpt_oss: "openai/gpt-oss-120b:free",
  llama: "meta-llama/llama-3.3-70b-instruct:free",
  qwen: "qwen/qwen3-next-80b-a3b-instruct:free",
  glm: "z-ai/glm-4.5-air:free",
};

const SLOT_ORDER: string[] = ["gpt_oss", "llama", "qwen", "glm"];

function avgLatency(latencies: number[]): number {
  if (latencies.length === 0) return 0;
  return Math.round(latencies.reduce((a, b) => a + b, 0) / latencies.length);
}

export default function SimulatePage({
  params,
}: {
  params: Promise<{ runId: string }>;
}): React.ReactElement {
  const { runId } = React.use(params);
  const { state, start } = useSimulateSocket(runId);
  const [config, setConfig] = React.useState({
    n_prompts: 8,
    domain: "specialty coffee retail",
    demo_mode: true,
  });

  function trigger(): void {
    start({
      n_prompts: config.n_prompts,
      domain: config.domain,
      demo_mode: config.demo_mode,
    });
  }

  const progressPct = state.total > 0 ? Math.min(100, Math.round((state.completed / state.total) * 100)) : 0;

  return (
    <SiteShell>
      <header className="mb-4 flex items-baseline justify-between gap-4">
        <div className="space-y-1">
          <p className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
            /simulate/{runId}
          </p>
          <h1 className="text-2xl font-bold tracking-tight">Agent face-off</h1>
        </div>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span
            className={
              state.ready
                ? "rounded-full bg-emerald-500/20 px-2 py-0.5 text-emerald-300"
                : "rounded-full bg-amber-500/20 px-2 py-0.5 text-amber-300"
            }
          >
            {state.ready ? "WS open" : "WS reconnecting"}
          </span>
          {state.done && (
            <span className="rounded-full bg-primary/20 px-2 py-0.5 text-primary">
              run complete - {state.totalCalls} calls
            </span>
          )}
        </div>
      </header>

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <label className="flex items-center gap-2 text-xs text-muted-foreground">
          <span className="font-mono">n_prompts</span>
          <input
            type="number"
            min={2}
            max={50}
            value={config.n_prompts}
            onChange={(e) =>
              setConfig((c) => ({ ...c, n_prompts: Math.max(2, Math.min(50, Number(e.target.value) || 8)) }))
            }
            className="w-16 rounded-md border border-border/60 bg-background px-2 py-1 text-right font-mono text-xs"
          />
        </label>
        <label className="flex items-center gap-2 text-xs text-muted-foreground">
          <input
            type="checkbox"
            checked={config.demo_mode}
            onChange={(e) => setConfig((c) => ({ ...c, demo_mode: e.target.checked }))}
            className="h-4 w-4 rounded border-border/60"
          />
          demo mode (caps to 10 prompts)
        </label>
        <Button onClick={trigger} disabled={!state.ready}>
          <Play className="mr-2 h-4 w-4" /> Run swarm
        </Button>
      </div>

      <div className="mb-4">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>Run progress</span>
          <span className="font-mono">
            {state.completed} / {state.total || "-"}
          </span>
        </div>
        <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-muted">
          <div
            className="h-full bg-primary transition-all duration-500"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
        {SLOT_ORDER.map((slot) => {
          const stats = state.bySlot[slot];
          const done = stats?.done ?? 0;
          const failed = stats?.parse_failed ?? 0;
          const failRate = done > 0 ? Math.round((failed / done) * 100) : 0;
          const lat = stats ? avgLatency(stats.latencies) : 0;
          return (
            <Card key={slot} className="border-border/60">
              <CardHeader className="space-y-1 pb-2">
                <CardTitle className="text-sm font-semibold">{SLOT_LABEL[slot] ?? slot}</CardTitle>
                <p className="truncate font-mono text-[11px] text-muted-foreground">
                  {SLOT_MODEL[slot] ?? slot}
                </p>
              </CardHeader>
              <CardContent>
                <div className="mb-3 grid grid-cols-3 gap-2 text-xs">
                  <div>
                    <div className="text-muted-foreground">Done</div>
                    <div className="font-mono text-lg font-bold">{done}</div>
                  </div>
                  <div>
                    <div className="text-muted-foreground">Avg ms</div>
                    <div className="font-mono text-lg font-bold">{lat || "-"}</div>
                  </div>
                  <div>
                    <div className="text-muted-foreground">Parse fail</div>
                    <div className="font-mono text-lg font-bold">{failRate}%</div>
                  </div>
                </div>
                <div className="h-[260px] overflow-y-auto rounded-md border border-border/40 bg-muted/20 p-2">
                  <ul className="space-y-1 text-xs">
                    {state.events
                      .filter((e) => e.slot === slot)
                      .slice(-30)
                      .reverse()
                      .map((e, i) => (
                        <li key={i} className="font-mono text-[10px]">
                          <span
                            className={
                              e.type === "agent_done"
                                ? "text-emerald-300"
                                : "text-muted-foreground"
                            }
                          >
                            {e.type}
                          </span>
                          <span className="ml-2 text-muted-foreground">
                            {e.buyer_prompt_id?.slice(0, 18) ?? ""}
                          </span>
                        </li>
                      ))}
                    {!stats && (
                      <li className="flex items-center gap-2 text-muted-foreground">
                        <Bot className="h-3.5 w-3.5" /> Waiting for prompts...
                      </li>
                    )}
                  </ul>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="mt-6 flex items-center gap-2 text-xs text-muted-foreground">
        <Activity className="h-3.5 w-3.5" />
        <span className="font-mono">live stream via /api/simulate/ws/{"{runId}"}</span>
      </div>
    </SiteShell>
  );
}
