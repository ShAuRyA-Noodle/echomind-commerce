"use client";

import * as React from "react";

import { CalibrationBadge } from "@/components/calibration-badge";
import type { CalibrationBucket } from "@/lib/colors";
import { cn } from "@/lib/utils";

/**
 * The reasoning-trace JSON shape from WINNING_PLAN §11. Mirrored to the
 * backend `api/schemas.py::ReasoningTrace`.
 */
export interface ReasoningStep {
  step: number;
  claim: string;
  source_node_ids: string[];
  confidence: number;
}

export interface KnowledgeSource {
  node_id: string;
  type: string;
  relevance: number;
}

export interface ContradictionResolution {
  between: string[];
  resolution: string;
}

export interface ReasoningTraceData {
  answer?: string | null;
  reasoning_chain: ReasoningStep[];
  knowledge_sources_used: KnowledgeSource[];
  contradictions_resolved: ContradictionResolution[];
  confidence: number;
  calibration: CalibrationBucket;
  uncertainty_type?: "data_sparse" | "data_contradictory" | "out_of_domain" | null;
}

export interface ReasoningTraceProps {
  trace: ReasoningTraceData;
  /** Called when a source-node link is clicked (jump to /graph). */
  onSourceClick?: (nodeId: string) => void;
  /** Auto-play step-by-step on mount. Default: true. */
  autoPlay?: boolean;
  /** ms per step. Default 800. */
  stepIntervalMs?: number;
  className?: string;
}

/**
 * Cinematic reasoning-trace animation - the originality moment from
 * WINNING_PLAN §19.3.
 *
 * Step 1 fades in → highlighted claim + glowing source-node chips → 800 ms
 * → Step 2 → … When all steps done, contradictions resolved appear and the
 * final calibration badge slides up. Click any source chip to jump to that
 * node in the graph view.
 */
export function ReasoningTrace({
  trace,
  onSourceClick,
  autoPlay = true,
  stepIntervalMs = 800,
  className,
}: ReasoningTraceProps): React.ReactElement {
  const [revealed, setRevealed] = React.useState<number>(autoPlay ? 0 : trace.reasoning_chain.length);
  const totalSteps = trace.reasoning_chain.length;

  React.useEffect(() => {
    if (!autoPlay || revealed >= totalSteps) return;
    const t = window.setTimeout(() => setRevealed((r) => r + 1), stepIntervalMs);
    return () => window.clearTimeout(t);
  }, [autoPlay, revealed, totalSteps, stepIntervalMs]);

  const allRevealed = revealed >= totalSteps;
  const showSources = allRevealed && trace.knowledge_sources_used.length > 0;
  const showContradictions = allRevealed && trace.contradictions_resolved.length > 0;

  return (
    <div className={cn("space-y-4", className)}>
      {trace.answer && (
        <div className="rounded-md border border-border/60 bg-muted/30 p-4">
          <p className="text-sm leading-relaxed">{trace.answer}</p>
        </div>
      )}

      <ol className="space-y-2">
        {trace.reasoning_chain.map((step, idx) => {
          const isVisible = idx < revealed;
          return (
            <li
              key={step.step}
              className={cn(
                "rounded-md border border-border/40 bg-card p-3 transition-all duration-500",
                isVisible
                  ? "translate-y-0 opacity-100"
                  : "translate-y-2 opacity-0"
              )}
              aria-hidden={!isVisible}
            >
              <div className="mb-1 flex items-center gap-2 text-xs text-muted-foreground">
                <span className="font-mono">step {step.step}</span>
                <span className="font-mono opacity-60">conf {step.confidence.toFixed(2)}</span>
              </div>
              <p className="text-sm leading-snug">{step.claim}</p>
              {step.source_node_ids.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {step.source_node_ids.map((nodeId) => (
                    <button
                      key={nodeId}
                      type="button"
                      onClick={() => onSourceClick?.(nodeId)}
                      className="rounded-sm border border-border/60 bg-muted/50 px-1.5 py-0.5 font-mono text-[10px] hover:bg-muted"
                      title="Jump to source node in /graph"
                    >
                      {nodeId.slice(0, 28)}
                    </button>
                  ))}
                </div>
              )}
            </li>
          );
        })}
      </ol>

      {showSources && (
        <details className="rounded-md border border-border/40 p-3">
          <summary className="cursor-pointer text-xs font-medium text-muted-foreground">
            Knowledge sources used ({trace.knowledge_sources_used.length})
          </summary>
          <ul className="mt-2 space-y-1 text-xs">
            {trace.knowledge_sources_used.map((src) => (
              <li key={src.node_id} className="flex items-center gap-2 font-mono">
                <button
                  type="button"
                  onClick={() => onSourceClick?.(src.node_id)}
                  className="text-left underline-offset-2 hover:underline"
                >
                  {src.node_id}
                </button>
                <span className="text-muted-foreground">{src.type}</span>
                <span className="ml-auto text-muted-foreground">
                  rel {src.relevance.toFixed(2)}
                </span>
              </li>
            ))}
          </ul>
        </details>
      )}

      {showContradictions && (
        <div className="rounded-md border border-destructive/40 bg-destructive/5 p-3">
          <p className="mb-1 text-xs font-medium text-destructive">
            Contradictions resolved ({trace.contradictions_resolved.length})
          </p>
          <ul className="space-y-1 text-xs">
            {trace.contradictions_resolved.map((c, idx) => (
              <li key={idx} className="font-mono text-muted-foreground">
                {c.between[0]} ↔ {c.between[1]}
                <span className="ml-2 text-foreground">- {c.resolution}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {allRevealed && (
        <div className="flex items-center gap-2 pt-1">
          <CalibrationBadge bucket={trace.calibration} score={trace.confidence} />
          {trace.uncertainty_type && (
            <span className="text-xs text-muted-foreground">
              {trace.uncertainty_type.replaceAll("_", " ")}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
