"use client";

import * as React from "react";
import dynamic from "next/dynamic";

import { NODE_COLORS, type NodeType } from "@/lib/colors";

// react-force-graph-2d is a client-only canvas component; SSR imports break.
const ForceGraph2D = dynamic(
  () => import("react-force-graph-2d").then((m) => m.default),
  { ssr: false, loading: () => <div className="h-full w-full animate-pulse bg-muted/30" /> }
);

export interface GraphNode {
  id: string;
  type?: NodeType | string;
  label?: string;
  confidence?: number;
  /** Set true for newly-arrived nodes; will pulse on entry. */
  fresh?: boolean;
}

export interface GraphEdge {
  source: string;
  target: string;
  type?: string;
  weight?: number;
}

export interface ForceGraphProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  width?: number;
  height?: number;
  onNodeClick?: (node: GraphNode) => void;
  /** Default true. Re-runs the d3 force simulation when nodes/edges change. */
  cooldownTicks?: number;
  className?: string;
}

const TYPE_FALLBACK_COLOR = "#94a3b8"; // slate-400

function nodeColorFor(node: GraphNode): string {
  const t = node.type as NodeType | undefined;
  if (t && t in NODE_COLORS) return NODE_COLORS[t];
  return TYPE_FALLBACK_COLOR;
}

function nodeRadius(node: GraphNode): number {
  const c = node.confidence ?? 0.7;
  return 4 + 6 * Math.max(0.2, Math.min(1.0, c));
}

/**
 * Reusable force-directed graph used by /graph (full viz) and /interview
 * (live mini-graph). Every node renders as a colored circle scaled by
 * confidence, with the label drawn on hover. Newly-arrived nodes pulse
 * for ~600ms (driven by the `fresh` flag).
 */
export function ForceGraph({
  nodes,
  edges,
  width,
  height = 520,
  onNodeClick,
  cooldownTicks = 50,
  className,
}: ForceGraphProps): React.ReactElement {
  const containerRef = React.useRef<HTMLDivElement | null>(null);
  const [containerWidth, setContainerWidth] = React.useState<number>(width ?? 800);
  const [pulseSet, setPulseSet] = React.useState<Set<string>>(new Set());

  // Resize observer keeps the canvas matching its container.
  React.useEffect(() => {
    if (typeof ResizeObserver === "undefined") return;
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(([entry]) => {
      if (entry) setContainerWidth(Math.max(320, Math.floor(entry.contentRect.width)));
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // Track fresh nodes to drive a pulse animation for ~600ms after arrival.
  React.useEffect(() => {
    const fresh = new Set<string>();
    for (const n of nodes) if (n.fresh) fresh.add(n.id);
    if (fresh.size === 0) return;
    setPulseSet((prev) => new Set([...prev, ...fresh]));
    const t = window.setTimeout(() => {
      setPulseSet((prev) => {
        const next = new Set(prev);
        for (const id of fresh) next.delete(id);
        return next;
      });
    }, 800);
    return () => window.clearTimeout(t);
  }, [nodes]);

  const data = React.useMemo(
    () => ({
      nodes: nodes.map((n) => ({ ...n })),
      links: edges.map((e) => ({ source: e.source, target: e.target, type: e.type, weight: e.weight ?? 1 })),
    }),
    [nodes, edges]
  );

  return (
    <div ref={containerRef} className={className} style={{ height, width: width ?? "100%" }}>
      <ForceGraph2D
        graphData={data}
        width={width ?? containerWidth}
        height={height}
        cooldownTicks={cooldownTicks}
        nodeRelSize={6}
        nodeLabel={(node: object) => {
          const n = node as GraphNode;
          return `${n.type ?? "Node"} - ${n.label ?? n.id}`;
        }}
        nodeCanvasObjectMode={() => "after"}
        nodeCanvasObject={(node: object, ctx: CanvasRenderingContext2D, scale: number) => {
          const n = node as GraphNode;
          const r = nodeRadius(n);
          const isPulse = pulseSet.has(n.id);
          if (isPulse) {
            ctx.beginPath();
            ctx.arc((n as { x?: number }).x ?? 0, (n as { y?: number }).y ?? 0, r * 1.8, 0, 2 * Math.PI, false);
            ctx.strokeStyle = nodeColorFor(n);
            ctx.lineWidth = 1.5 / scale;
            ctx.globalAlpha = 0.6;
            ctx.stroke();
            ctx.globalAlpha = 1.0;
          }
          if (scale > 1.2 && n.label) {
            const label = n.label.length > 32 ? `${n.label.slice(0, 32)}...` : n.label;
            ctx.font = `${10 / scale}px system-ui, sans-serif`;
            ctx.fillStyle = "rgba(255,255,255,0.85)";
            ctx.textAlign = "center";
            ctx.fillText(label, (n as { x?: number }).x ?? 0, ((n as { y?: number }).y ?? 0) + r + 8 / scale);
          }
        }}
        nodeColor={(n: object) => nodeColorFor(n as GraphNode)}
        linkColor={() => "rgba(255,255,255,0.15)"}
        linkWidth={(l: object) => 0.5 + Math.min(2, ((l as { weight?: number }).weight ?? 1))}
        linkDirectionalParticles={0}
        backgroundColor="transparent"
        onNodeClick={(node: object) => onNodeClick?.(node as GraphNode)}
      />
    </div>
  );
}
