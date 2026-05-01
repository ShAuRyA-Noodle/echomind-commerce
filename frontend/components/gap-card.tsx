import * as React from "react";

import { CalibrationBadge } from "@/components/calibration-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { CalibrationBucket } from "@/lib/colors";
import { cn } from "@/lib/utils";

/**
 * Five canonical gap types, per WINNING_PLAN §16.1.
 * Aligned 1:1 with backend `api/schemas.py::GapType`.
 */
export type GapType =
  | "omission"
  | "contradiction"
  | "ambiguity"
  | "hallucination"
  | "dark_zone";

export interface GapCardProps {
  title: string;
  type: GapType;
  severity: number; // 0-1
  revenueAtRisk: number; // USD
  calibration: CalibrationBucket;
  affectedProducts: number;
  /** Optional one-line "why this matters" - surfaces in the card. */
  blurb?: string;
  onGenerateFix?: () => void;
  onOpenDeepDive?: () => void;
  className?: string;
}

const GAP_TYPE_LABEL: Record<GapType, string> = {
  omission: "Omission",
  contradiction: "Contradiction",
  ambiguity: "Ambiguity",
  hallucination: "Hallucination",
  dark_zone: "Dark zone",
};

const GAP_TYPE_HELP: Record<GapType, string> = {
  omission: "Product has clear positioning but no agent surfaces it.",
  contradiction: "Merchant statement contradicts agent claim about same product.",
  ambiguity: "Agents disagree about the same product.",
  hallucination: "Agent invents a feature, accessory, or policy that does not exist.",
  dark_zone: "Entire subcategory invisible to all agents.",
};

function formatUsd(n: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);
}

/**
 * Audit-dashboard gap card. Aligned with WINNING_PLAN §20.3.
 *
 * Encodes:
 *   * gap type label (5 canonical types)
 *   * severity bar (0-100%)
 *   * monthly revenue-at-risk (currency-formatted)
 *   * 5-bucket calibration badge - including a visible "Don't know" state,
 *     which is the core product principle (calibrated honesty over inflated
 *     numbers, see §9.4).
 *   * affected product count
 *   * actions: generate fix / open deep dive
 */
export function GapCard({
  title,
  type,
  severity,
  revenueAtRisk,
  calibration,
  affectedProducts,
  blurb,
  onGenerateFix,
  onOpenDeepDive,
  className,
}: GapCardProps): React.ReactElement {
  const severityPct = Math.round(severity * 100);
  const isDontKnow = calibration === "dont_know";

  return (
    <Card className={cn("border-border/60", className)}>
      <CardHeader className="space-y-2 pb-3">
        <div className="flex items-center justify-between gap-2">
          <Badge
            variant="outline"
            className="font-mono text-[10px] uppercase tracking-wide"
            title={GAP_TYPE_HELP[type]}
          >
            {GAP_TYPE_LABEL[type]}
          </Badge>
          <CalibrationBadge bucket={calibration} />
        </div>
        <CardTitle className="text-lg leading-snug">{title}</CardTitle>
        {blurb && (
          <p className="text-sm leading-snug text-muted-foreground">{blurb}</p>
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <div className="mb-1 flex items-center justify-between text-xs text-muted-foreground">
            <span>Severity</span>
            <span className="font-mono">{severityPct}%</span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
            <div
              className="h-full bg-[hsl(var(--destructive))]"
              style={{ width: `${severityPct}%` }}
            />
          </div>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">$ at risk / month</span>
          <span className="font-mono font-semibold">
            {isDontKnow ? "-" : formatUsd(revenueAtRisk)}
          </span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Products affected</span>
          <span className="font-mono">{affectedProducts}</span>
        </div>
        {isDontKnow && (
          <p className="rounded-md border border-dashed border-border/60 bg-muted/30 p-2 text-xs text-muted-foreground">
            Not enough evidence in the graph to estimate impact. Run a longer
            interview or broader simulation to enable scoring.
          </p>
        )}
        <div className="flex gap-2">
          {onOpenDeepDive && (
            <Button
              onClick={onOpenDeepDive}
              variant="outline"
              size="sm"
              className="flex-1"
            >
              Deep dive
            </Button>
          )}
          {onGenerateFix && !isDontKnow && (
            <Button onClick={onGenerateFix} className="flex-1" size="sm">
              Generate fix
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
