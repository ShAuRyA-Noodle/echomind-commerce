"use client";

import * as React from "react";
import { Network, Search } from "lucide-react";

import { ForceGraph, type GraphNode, type GraphEdge } from "@/components/force-graph";
import { SiteShell } from "@/components/site-shell";
import { Button } from "@/components/ui/button";
import { apiClient } from "@/lib/api-client";
import { NODE_COLORS, type NodeType } from "@/lib/colors";

interface ApiGraphResponse {
  status: string;
  store_id: string;
  nodes: Array<{ id: string; type: string; label?: string; confidence?: number }>;
  edges: Array<{ source: string; target: string; type?: string; weight?: number }>;
}

interface ApiNodeDetail {
  status: string;
  node?: Record<string, unknown> | null;
  neighbors: Array<{
    source_id: string;
    neighbor_id: string;
    neighbor_type: string;
    neighbor_label: string;
    rel_type: string;
  }>;
}

const NODE_TYPES = Object.keys(NODE_COLORS) as NodeType[];

export default function GraphPage({ params }: { params: { storeId: string } }): React.ReactElement {
  const [nodes, setNodes] = React.useState<GraphNode[]>([]);
  const [edges, setEdges] = React.useState<GraphEdge[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [filter, setFilter] = React.useState<Set<NodeType>>(new Set(NODE_TYPES));
  const [query, setQuery] = React.useState("");
  const [selected, setSelected] = React.useState<ApiNodeDetail | null>(null);

  const refresh = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await apiClient.request<ApiGraphResponse>({
        path: `/api/graph/${params.storeId}`,
        query: { limit: 600 },
      });
      setNodes(
        r.nodes.map((n) => ({
          id: n.id,
          type: n.type,
          label: n.label ?? n.id,
          confidence: n.confidence,
        }))
      );
      setEdges(r.edges.map((e) => ({ ...e })));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, [params.storeId]);

  React.useEffect(() => {
    refresh();
  }, [refresh]);

  function toggleType(t: NodeType): void {
    setFilter((prev) => {
      const next = new Set(prev);
      if (next.has(t)) {
        next.delete(t);
      } else {
        next.add(t);
      }
      return next;
    });
  }

  const filteredNodes = React.useMemo(() => {
    return nodes.filter((n) => {
      if (n.type && !filter.has(n.type as NodeType)) return false;
      if (query.trim() && !(n.label ?? "").toLowerCase().includes(query.toLowerCase())) return false;
      return true;
    });
  }, [nodes, filter, query]);

  const visibleIds = React.useMemo(() => new Set(filteredNodes.map((n) => n.id)), [filteredNodes]);
  const filteredEdges = React.useMemo(
    () => edges.filter((e) => visibleIds.has(e.source) && visibleIds.has(e.target)),
    [edges, visibleIds]
  );

  async function onNodeClick(node: GraphNode): Promise<void> {
    try {
      const detail = await apiClient.request<ApiNodeDetail>({
        path: `/api/graph/${params.storeId}/node/${encodeURIComponent(node.id)}`,
      });
      setSelected(detail);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  return (
    <SiteShell>
      <header className="mb-4 flex items-baseline justify-between">
        <div className="space-y-1">
          <p className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
            /graph/{params.storeId}
          </p>
          <h1 className="text-2xl font-bold tracking-tight">Commerce graph</h1>
        </div>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span className="font-mono">
            {filteredNodes.length} nodes - {filteredEdges.length} edges
          </span>
          <Button size="sm" variant="outline" onClick={refresh} disabled={loading}>
            {loading ? "Loading..." : "Reload"}
          </Button>
        </div>
      </header>

      <div className="grid grid-cols-12 gap-4">
        <aside className="col-span-12 space-y-4 lg:col-span-3">
          <div className="rounded-lg border border-border/60 bg-card/40 p-4">
            <div className="mb-3 flex items-center gap-2 text-xs uppercase tracking-wider text-muted-foreground">
              <Search className="h-3.5 w-3.5" />
              Search
            </div>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="filter by label..."
              className="w-full rounded-md border border-border/60 bg-background px-2 py-1 text-sm"
            />
          </div>
          <div className="rounded-lg border border-border/60 bg-card/40 p-4">
            <div className="mb-3 font-mono text-xs uppercase tracking-wider text-muted-foreground">
              Node types
            </div>
            <ul className="space-y-2 text-xs">
              {NODE_TYPES.map((t) => (
                <li key={t}>
                  <button
                    type="button"
                    onClick={() => toggleType(t)}
                    className={
                      "flex w-full items-center gap-2 rounded-md px-1 py-0.5 text-left transition-colors " +
                      (filter.has(t) ? "" : "opacity-40")
                    }
                  >
                    <span
                      className="inline-block h-2.5 w-2.5 rounded-full"
                      style={{ backgroundColor: NODE_COLORS[t] }}
                    />
                    <span className="font-mono">{t}</span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
          {selected && (
            <div className="rounded-lg border border-border/60 bg-card/40 p-4 text-xs">
              <div className="mb-2 font-mono uppercase tracking-wider text-muted-foreground">
                Selected node
              </div>
              <p className="font-mono break-all">
                {String(((selected.node as { id?: string } | null)?.id) ?? "")}
              </p>
              <p className="mt-2 text-muted-foreground">
                {selected.neighbors.length} neighbors
              </p>
              <ul className="mt-1 max-h-40 space-y-0.5 overflow-y-auto">
                {selected.neighbors.slice(0, 20).map((n, i) => (
                  <li key={i} className="font-mono text-[10px]">
                    <span className="text-muted-foreground">{n.rel_type}</span>{" "}
                    {n.neighbor_label?.slice(0, 32)}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </aside>
        <section className="col-span-12 lg:col-span-9">
          <div className="rounded-lg border border-border/60 bg-card/30 p-2">
            {error ? (
              <div className="p-6 text-center text-sm text-destructive">{error}</div>
            ) : loading && filteredNodes.length === 0 ? (
              <div className="flex h-[640px] items-center justify-center text-sm text-muted-foreground">
                <Network className="mr-2 h-4 w-4" /> Loading graph...
              </div>
            ) : filteredNodes.length === 0 ? (
              <div className="flex h-[640px] items-center justify-center text-sm text-muted-foreground">
                Empty graph. Run /api/onboard/ingest/run to seed.
              </div>
            ) : (
              <ForceGraph
                nodes={filteredNodes}
                edges={filteredEdges}
                height={640}
                onNodeClick={(n) => onNodeClick(n)}
              />
            )}
          </div>
        </section>
      </div>
    </SiteShell>
  );
}
