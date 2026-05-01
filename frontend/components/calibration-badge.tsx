import * as React from "react";

import { CALIBRATION_STYLES, type CalibrationBucket } from "@/lib/colors";
import { cn } from "@/lib/utils";

export interface CalibrationBadgeProps {
  bucket: CalibrationBucket;
  /** Optional numeric score (0-1) to render alongside the bucket label. */
  score?: number;
  className?: string;
}

/**
 * 5-bucket calibration badge.
 * Color-coded per WINNING_PLAN §20.2: certain (green) → confident (lime) →
 * uncertain (amber) → low_confidence (orange) → dont_know (grey, striped).
 */
export function CalibrationBadge({
  bucket,
  score,
  className,
}: CalibrationBadgeProps): React.ReactElement {
  const style = CALIBRATION_STYLES[bucket];
  const isStriped = style.striped;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold",
        isStriped && "calibration-stripe",
        className,
      )}
      style={
        isStriped
          ? { color: style.textColor }
          : { backgroundColor: style.color, color: style.textColor }
      }
      title={`Calibration: ${style.label}`}
    >
      <span
        aria-hidden
        className="inline-block h-1.5 w-1.5 rounded-full"
        style={{ backgroundColor: style.textColor, opacity: 0.85 }}
      />
      <span>{style.label}</span>
      {typeof score === "number" && (
        <span className="font-mono opacity-80">{score.toFixed(2)}</span>
      )}
    </span>
  );
}
