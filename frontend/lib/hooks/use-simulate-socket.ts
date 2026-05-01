"use client";

import { useEffect, useRef, useState } from "react";

import {
  createWsClient,
  simulateWsPath,
  type BackendEvent,
  type WsClient,
} from "@/lib/ws-client";

export interface AgentDoneEvent {
  slot: string;
  buyer_prompt_id: string;
  latency_ms: number;
  parse_failed: boolean;
  error?: string | null;
}

export interface UseSimulateSocketState {
  ready: boolean;
  starting: boolean;
  completed: number;
  total: number;
  bySlot: Record<string, { done: number; parse_failed: number; latencies: number[] }>;
  events: { ts: number; type: string; slot?: string; buyer_prompt_id?: string }[];
  done: boolean;
  totalCalls: number;
  buyerPrompts: number;
  lastError: string | null;
}

export interface SwarmRunConfig {
  n_prompts?: number;
  domain?: string;
  catalog_excerpt?: string;
  policies_summary?: string;
  product_categories?: string[];
  merchant_truths_summary?: unknown[];
  customer_questions?: unknown[];
  demo_mode?: boolean;
}

export interface UseSimulateSocketHandle {
  state: UseSimulateSocketState;
  start: (cfg?: SwarmRunConfig) => void;
  close: () => void;
}

/**
 * Connects to /api/simulate/ws/{runId} and reduces its event stream into a
 * flat per-slot state for the 4-column UI. Persists `agent_done` rows so
 * the demo can rewind by-slot completion order.
 */
export function useSimulateSocket(runId: string): UseSimulateSocketHandle {
  const wsRef = useRef<WsClient | null>(null);
  const [state, setState] = useState<UseSimulateSocketState>({
    ready: false,
    starting: false,
    completed: 0,
    total: 0,
    bySlot: {},
    events: [],
    done: false,
    totalCalls: 0,
    buyerPrompts: 0,
    lastError: null,
  });

  useEffect(() => {
    if (!runId) return;
    const ws = createWsClient({
      path: simulateWsPath(runId),
      onOpen: () => setState((s) => ({ ...s, ready: true })),
    });
    wsRef.current = ws;

    const subs = [
      ws.subscribe("run_open", () => {
        setState((s) => ({ ...s, ready: true }));
      }),
      ws.subscribe("agent_start", (e: BackendEvent) => {
        const slot = String(e.slot ?? "?");
        const buyer_prompt_id = String(e.buyer_prompt_id ?? "");
        setState((s) => ({
          ...s,
          events: [
            ...s.events,
            { ts: Date.now(), type: "agent_start", slot, buyer_prompt_id },
          ],
        }));
      }),
      ws.subscribe("agent_done", (e: BackendEvent) => {
        const slot = String(e.slot ?? "?");
        const latency = Number(e.latency_ms ?? 0);
        const parseFailed = Boolean(e.parse_failed);
        setState((s) => {
          const cur = s.bySlot[slot] ?? { done: 0, parse_failed: 0, latencies: [] };
          return {
            ...s,
            bySlot: {
              ...s.bySlot,
              [slot]: {
                done: cur.done + 1,
                parse_failed: cur.parse_failed + (parseFailed ? 1 : 0),
                latencies: [...cur.latencies, latency],
              },
            },
            events: [
              ...s.events,
              { ts: Date.now(), type: "agent_done", slot },
            ],
          };
        });
      }),
      ws.subscribe("run_progress", (e: BackendEvent) => {
        setState((s) => ({
          ...s,
          completed: Number(e.completed ?? s.completed),
          total: Number(e.total ?? s.total),
        }));
      }),
      ws.subscribe("run_complete", (e: BackendEvent) => {
        setState((s) => ({
          ...s,
          done: true,
          totalCalls: Number(e.total_calls ?? s.totalCalls),
          buyerPrompts: Number(e.buyer_prompts ?? s.buyerPrompts),
        }));
      }),
      ws.subscribe("error", (e: BackendEvent) => {
        setState((s) => ({ ...s, lastError: (e.message as string) ?? "unknown error" }));
      }),
    ];

    return () => {
      for (const u of subs) u();
      ws.close();
      wsRef.current = null;
    };
  }, [runId]);

  function start(cfg?: SwarmRunConfig): void {
    if (!wsRef.current) return;
    setState((s) => ({ ...s, starting: true }));
    wsRef.current.send({ type: "control", action: "start", config: cfg ?? { demo_mode: true } });
  }

  function close(): void {
    wsRef.current?.close();
  }

  return { state, start, close };
}
