"use client";

import { useEffect, useRef, useState } from "react";

import {
  createWsClient,
  interviewWsPath,
  type BackendEvent,
  type WsClient,
} from "@/lib/ws-client";

export interface InterviewQuestion {
  text: string;
  follow_up_if_brief?: string | null;
  phase: string;
  phase_label: string;
}

export interface GraphAdded {
  type: string;
  id: string;
  label?: string;
}

export interface InterviewProgress {
  question_count: number;
  elapsed_minutes: number;
  graph_stats: {
    nodes?: Record<string, number>;
    edges?: Record<string, number>;
  };
}

export interface UseInterviewSocketState {
  ready: boolean;
  phase: string;
  phaseLabel: string;
  question: InterviewQuestion | null;
  transcript: { speaker: "M" | "I"; text: string }[];
  added: GraphAdded[];
  progress: InterviewProgress | null;
  parseFailed: boolean;
  lastError: string | null;
}

export interface UseInterviewSocketHandle {
  state: UseInterviewSocketState;
  start: () => void;
  nextQuestion: () => void;
  advancePhase: () => void;
  sendText: (text: string) => void;
  close: () => void;
}

/**
 * Connects to /api/interview/ws/{sessionId} and surfaces a flat React state.
 *
 * Server emits per WINNING_PLAN section 5.5:
 *   session_open / transcript / question / extraction / graph_update /
 *   phase_change / progress / error
 */
export function useInterviewSocket(sessionId: string): UseInterviewSocketHandle {
  const wsRef = useRef<WsClient | null>(null);
  const [state, setState] = useState<UseInterviewSocketState>({
    ready: false,
    phase: "brand_mapping",
    phaseLabel: "Brand Mapping",
    question: null,
    transcript: [],
    added: [],
    progress: null,
    parseFailed: false,
    lastError: null,
  });

  useEffect(() => {
    if (!sessionId) return;
    const ws = createWsClient({
      path: interviewWsPath(sessionId),
      onOpen: () => setState((s) => ({ ...s, ready: true })),
    });
    wsRef.current = ws;

    const subs = [
      ws.subscribe("session_open", (e: BackendEvent) => {
        setState((s) => ({
          ...s,
          phase: (e.phase as string) ?? s.phase,
          phaseLabel: (e.phase_label as string) ?? s.phaseLabel,
        }));
      }),
      ws.subscribe("transcript", (e: BackendEvent) => {
        const speaker = (e.speaker as "M" | "I") ?? "M";
        const text = (e.text as string) ?? "";
        if (!text) return;
        setState((s) => ({ ...s, transcript: [...s.transcript, { speaker, text }] }));
      }),
      ws.subscribe("question", (e: BackendEvent) => {
        setState((s) => ({
          ...s,
          question: {
            text: (e.text as string) ?? "",
            follow_up_if_brief: (e.follow_up_if_brief as string) ?? null,
            phase: (e.phase as string) ?? s.phase,
            phase_label: (e.phase_label as string) ?? s.phaseLabel,
          },
          phase: (e.phase as string) ?? s.phase,
          phaseLabel: (e.phase_label as string) ?? s.phaseLabel,
          transcript: [
            ...s.transcript,
            { speaker: "I", text: (e.text as string) ?? "" },
          ],
        }));
      }),
      ws.subscribe("extraction", (e: BackendEvent) => {
        setState((s) => ({ ...s, parseFailed: Boolean(e.parse_failed) }));
      }),
      ws.subscribe("graph_update", (e: BackendEvent) => {
        const added = (e.added as GraphAdded[]) ?? [];
        setState((s) => ({ ...s, added: [...s.added, ...added] }));
      }),
      ws.subscribe("phase_change", (e: BackendEvent) => {
        setState((s) => ({
          ...s,
          phase: (e.phase as string) ?? s.phase,
          phaseLabel: (e.phase_label as string) ?? s.phaseLabel,
        }));
      }),
      ws.subscribe("progress", (e: BackendEvent) => {
        setState((s) => ({
          ...s,
          progress: {
            question_count: (e.question_count as number) ?? s.progress?.question_count ?? 0,
            elapsed_minutes: (e.elapsed_minutes as number) ?? s.progress?.elapsed_minutes ?? 0,
            graph_stats:
              (e.graph_stats as InterviewProgress["graph_stats"]) ?? s.progress?.graph_stats ?? {},
          },
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
  }, [sessionId]);

  function start(): void {
    wsRef.current?.send({ type: "control", action: "start" });
  }
  function nextQuestion(): void {
    wsRef.current?.send({ type: "control", action: "next_question" });
  }
  function advancePhase(): void {
    wsRef.current?.send({ type: "control", action: "advance_phase" });
  }
  function sendText(text: string): void {
    if (!text.trim()) return;
    wsRef.current?.send({ type: "text_input", text });
  }
  function close(): void {
    wsRef.current?.close();
  }

  return { state, start, nextQuestion, advancePhase, sendText, close };
}
