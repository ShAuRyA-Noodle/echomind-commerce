/**
 * Echomind color palette - single source of truth.
 * Mirrors the CSS vars in app/globals.css. Use these for canvas/SVG/JS
 * contexts where Tailwind class binding doesn't work (e.g. ForceGraph2D).
 *
 * Per WINNING_PLAN.md §20.2.
 */

export type NodeType =
  | "Product"
  | "Policy"
  | "TrustSignal"
  | "MerchantTruth"
  | "Decision"
  | "Pattern"
  | "CustomerQuestion"
  | "BuyerPrompt"
  | "AgentRepresentation"
  | "Gap"
  | "FixSuggestion";

export const NODE_COLORS: Record<NodeType, string> = {
  Product: "#3B82F6",
  Policy: "#F59E0B",
  TrustSignal: "#10B981",
  MerchantTruth: "#8B5CF6",
  Decision: "#F43F5E",
  Pattern: "#06B6D4",
  CustomerQuestion: "#EAB308",
  BuyerPrompt: "#A855F7", // violet - distinct from MerchantTruth purple
  AgentRepresentation: "#EC4899",
  Gap: "#EF4444",
  FixSuggestion: "#22C55E",
};

export type CalibrationBucket =
  | "certain"
  | "confident"
  | "uncertain"
  | "low_confidence"
  | "dont_know";

export interface CalibrationStyle {
  label: string;
  color: string;
  textColor: string;
  /** dont_know is rendered with a striped pattern */
  striped: boolean;
}

export const CALIBRATION_STYLES: Record<CalibrationBucket, CalibrationStyle> = {
  certain: {
    label: "Certain",
    color: "#16A34A", // green-600
    textColor: "#FFFFFF",
    striped: false,
  },
  confident: {
    label: "Confident",
    color: "#84CC16", // lime-500
    textColor: "#0A0A0A",
    striped: false,
  },
  uncertain: {
    label: "Uncertain",
    color: "#F59E0B", // amber-500
    textColor: "#0A0A0A",
    striped: false,
  },
  low_confidence: {
    label: "Low confidence",
    color: "#F97316", // orange-500
    textColor: "#FFFFFF",
    striped: false,
  },
  dont_know: {
    label: "Don't know",
    color: "#6B7280", // gray-500
    textColor: "#FFFFFF",
    striped: true,
  },
};

export function nodeColor(type: NodeType): string {
  return NODE_COLORS[type];
}

export function calibrationStyle(bucket: CalibrationBucket): CalibrationStyle {
  return CALIBRATION_STYLES[bucket];
}
