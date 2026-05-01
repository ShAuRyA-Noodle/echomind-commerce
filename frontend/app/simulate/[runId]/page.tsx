import { Bot } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { SiteShell } from "@/components/site-shell";

const AGENTS = [
  { name: "Llama 3.3 70B", model: "meta-llama/llama-3.3-70b-instruct:free" },
  { name: "Qwen 2.5 72B", model: "qwen/qwen-2.5-72b-instruct:free" },
  { name: "DeepSeek Chat", model: "deepseek/deepseek-chat:free" },
  { name: "Gemini 2.0 Flash", model: "google/gemini-2.0-flash-exp:free" },
];

export default function SimulatePage({
  params,
}: {
  params: { runId: string };
}): JSX.Element {
  return (
    <SiteShell>
      <header className="mb-6 flex items-baseline justify-between">
        <div className="space-y-1">
          <p className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
            /simulate/{params.runId}
          </p>
          <h1 className="text-2xl font-bold tracking-tight">Agent face-off</h1>
        </div>
        <p className="text-sm text-muted-foreground">4 columns · streaming · coming Day 8</p>
      </header>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
        {AGENTS.map((agent) => (
          <div key={agent.name} className="space-y-3">
            <div className="rounded-lg border border-border/60 bg-card/40 px-4 py-3">
              <div className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
                Agent
              </div>
              <div className="mt-1 text-sm font-semibold">{agent.name}</div>
              <div className="mt-0.5 truncate font-mono text-[11px] text-muted-foreground">
                {agent.model}
              </div>
            </div>
            <EmptyState
              icon={Bot}
              title="Streaming responses"
              description="Surface rate, sentiment, and verbatim samples will stream here."
              className="h-[420px]"
            />
          </div>
        ))}
      </div>
    </SiteShell>
  );
}
