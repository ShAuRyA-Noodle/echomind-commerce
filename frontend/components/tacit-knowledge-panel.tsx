"use client";

import * as React from "react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

/**
 * Tacit Knowledge Capture Score panel (WINNING_PLAN §19.4).
 *
 * Quantifies how much of the merchant's tacit knowledge the interview
 * surfaced, broken down by the six categories of the WINNING_PLAN §7
 * Tacit Knowledge Taxonomy. Each category has a target count; we display
 * captured/target as a horizontal bar.
 *
 * The "What I Didn't Know I Knew" report is rendered below - surfaces the
 * top 3 MerchantTruths the merchant rated as surprising in the post-
 * interview Living Update Loop (§12).
 */

export type TacitCategory =
  | "procedural"
  | "conditional_heuristic"
  | "experiential_pattern"
  | "intuitive_judgment"
  | "edge_case_knowledge"
  | "meta_knowledge";

const CATEGORY_LABEL: Record<TacitCategory, string> = {
  procedural: "Procedural",
  conditional_heuristic: "Conditional Heuristic",
  experiential_pattern: "Experiential Pattern",
  intuitive_judgment: "Intuitive Judgment",
  edge_case_knowledge: "Edge Case Knowledge",
  meta_knowledge: "Meta-Knowledge",
};

const CATEGORY_HELP: Record<TacitCategory, string> = {
  procedural: "Explicit operational steps the merchant could have written down.",
  conditional_heuristic: "If-X-then-Y rules of thumb.",
  experiential_pattern: "Customers who do X tend to Y patterns.",
  intuitive_judgment: "Gut feelings the merchant cannot fully justify.",
  edge_case_knowledge: "Exceptions to standard rules.",
  meta_knowledge: "What the merchant knows they don't know.",
};

// Target counts per category for the score (tunable per vertical).
const DEFAULT_TARGETS: Record<TacitCategory, number> = {
  procedural: 8,
  conditional_heuristic: 8,
  experiential_pattern: 6,
  intuitive_judgment: 4,
  edge_case_knowledge: 6,
  meta_knowledge: 3,
};

export interface SurprisingTruth {
  id: string;
  statement: string;
  tacit_category: TacitCategory;
}

export interface TacitKnowledgePanelProps {
  /** Captured count per category. */
  captured: Partial<Record<TacitCategory, number>>;
  /** Optional override of the target counts (defaults are conservative). */
  targets?: Partial<Record<TacitCategory, number>>;
  /** Top truths the merchant flagged as "didn't know I knew this". */
  surprising?: SurprisingTruth[];
  className?: string;
}

export function TacitKnowledgePanel({
  captured,
  targets,
  surprising,
  className,
}: TacitKnowledgePanelProps): React.ReactElement {
  const targetMap = { ...DEFAULT_TARGETS, ...targets };
  const cats = Object.keys(targetMap) as TacitCategory[];

  const totals = cats.reduce(
    (acc, c) => {
      acc.captured += captured[c] ?? 0;
      acc.target += targetMap[c];
      return acc;
    },
    { captured: 0, target: 0 }
  );
  const overallPct = totals.target > 0 ? Math.min(100, Math.round((totals.captured / totals.target) * 100)) : 0;

  return (
    <Card className={cn("border-border/60", className)}>
      <CardHeader className="space-y-1">
        <CardTitle className="text-base">Tacit Knowledge Capture</CardTitle>
        <p className="text-xs text-muted-foreground">
          You captured {totals.captured} of an estimated {totals.target} truths - {overallPct}%
          of your domain brain. Distributed across the six tacit-knowledge categories below.
        </p>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center gap-3">
          <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-[hsl(var(--primary))] transition-all duration-700"
              style={{ width: `${overallPct}%` }}
            />
          </div>
          <span className="font-mono text-sm tabular-nums">{overallPct}%</span>
        </div>

        <ul className="space-y-2">
          {cats.map((c) => {
            const cap = captured[c] ?? 0;
            const tgt = targetMap[c];
            const pct = tgt > 0 ? Math.min(100, Math.round((cap / tgt) * 100)) : 0;
            return (
              <li key={c} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span title={CATEGORY_HELP[c]}>{CATEGORY_LABEL[c]}</span>
                  <span className="font-mono tabular-nums text-muted-foreground">
                    {cap} / {tgt}
                  </span>
                </div>
                <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                  <div
                    className="h-full rounded-full bg-[var(--node-merchant-truth)] transition-all duration-700"
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </li>
            );
          })}
        </ul>

        {surprising && surprising.length > 0 && (
          <div className="mt-2 rounded-md border border-dashed border-border/50 bg-muted/20 p-3">
            <p className="mb-2 text-xs font-medium text-muted-foreground">
              What you didn't know you knew
            </p>
            <ul className="space-y-1">
              {surprising.slice(0, 3).map((t) => (
                <li key={t.id} className="text-xs leading-snug">
                  <span className="text-muted-foreground">[{CATEGORY_LABEL[t.tacit_category]}]</span>
                  <span className="ml-1">{t.statement}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
