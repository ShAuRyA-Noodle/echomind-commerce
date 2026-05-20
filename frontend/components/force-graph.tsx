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
  cooldownTicks?: number;
  /** Auto-zoom to fit all nodes after simulation settles. Default true. */
  autoFit?: boolean;
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
  cooldownTicks = 80,
  autoFit = true,
  className,
}: ForceGraphProps): React.ReactElement {
  const containerRef = React.useRef<HTMLDivElement | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const graphRef = React.useRef<any>(null);
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
    <div ref={containerRef} className={className} style={{ height, width: width ?? "100%", position: "relative" }}>
      <ForceGraph2D
        ref={graphRef}
        graphData={data}
        width={width ?? containerWidth}
        height={height}
        cooldownTicks={cooldownTicks}
        onEngineStop={() => {
          if (autoFit && graphRef.current && nodes.length > 0) {
            graphRef.current.zoomToFit(400, 24);
          }
        }}
        nodeRelSize={5}
        nodeLabel={(node: object) => {
          const n = node as GraphNode;
          return `${n.type ?? "Node"}: ${n.label ?? n.id}`;
        }}
        nodeCanvasObjectMode={() => "after"}
        nodeCanvasObject={(node: object, ctx: CanvasRenderingContext2D, scale: number) => {
          const n = node as GraphNode;
          const r = nodeRadius(n);
          const isPulse = pulseSet.has(n.id);
          if (isPulse) {
            ctx.beginPath();
            ctx.arc((n as { x?: number }).x ?? 0, (n as { y?: number }).y ?? 0, r * 2.2, 0, 2 * Math.PI, false);
            ctx.strokeStyle = nodeColorFor(n);
            ctx.lineWidth = 2 / scale;
            ctx.globalAlpha = 0.7;
            ctx.stroke();
            ctx.globalAlpha = 1.0;
          }
          // Always show label (not just on zoom) for mini-graph readability
          if (n.label) {
            const label = n.label.length > 22 ? `${n.label.slice(0, 22)}...` : n.label;
            const fontSize = Math.max(8, Math.min(11, 10 / (scale || 1)));
            ctx.font = `${fontSize}px system-ui, sans-serif`;
            ctx.fillStyle = "rgba(255,255,255,0.9)";
            ctx.textAlign = "center";
            ctx.fillText(label, (n as { x?: number }).x ?? 0, ((n as { y?: number }).y ?? 0) + r + fontSize + 2);
          }
        }}
        nodeColor={(n: object) => nodeColorFor(n as GraphNode)}
        linkColor={() => "rgba(255,255,255,0.2)"}
        linkWidth={(l: object) => 0.8 + Math.min(2, ((l as { weight?: number }).weight ?? 1))}
        linkDirectionalArrowLength={3}
        linkDirectionalArrowRelPos={1}
        linkDirectionalParticles={0}
        backgroundColor="transparent"
        enableZoomInteraction
        enablePanInteraction
        onNodeClick={(node: object) => onNodeClick?.(node as GraphNode)}
      />
      {/* Zoom controls overlay */}
      <div style={{ position: "absolute", top: 8, right: 8, display: "flex", flexDirection: "column", gap: 4 }}>
        <button
          type="button"
          onClick={() => graphRef.current?.zoom(1.4, 200)}
          style={{
            width: 28, height: 28, borderRadius: 6,
            background: "rgba(255,255,255,0.1)", border: "1px solid rgba(255,255,255,0.2)",
            color: "white", fontSize: 18, cursor: "pointer", lineHeight: 1,
          }}
        >+</button>
        <button
          type="button"
          onClick={() => graphRef.current?.zoom(0.7, 200)}
          style={{
            width: 28, height: 28, borderRadius: 6,
            background: "rgba(255,255,255,0.1)", border: "1px solid rgba(255,255,255,0.2)",
            color: "white", fontSize: 18, cursor: "pointer", lineHeight: 1,
          }}
        >-</button>
        <button
          type="button"
          onClick={() => nodes.length > 0 && graphRef.current?.zoomToFit(400, 24)}
          style={{
            width: 28, height: 28, borderRadius: 6,
            background: "rgba(255,255,255,0.1)", border: "1px solid rgba(255,255,255,0.2)",
            color: "white", fontSize: 11, cursor: "pointer", lineHeight: 1,
          }}
          title="Fit all"
        >⊡</button>
      </div>
    </div>
  );
}
