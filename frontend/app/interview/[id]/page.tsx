"use client";

import * as React from "react";
import { Mic, MessageSquare, Network, Play, SkipForward, ChevronRight } from "lucide-react";

import { ForceGraph, type GraphNode, type GraphEdge } from "@/components/force-graph";
import { SiteShell } from "@/components/site-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useInterviewSocket } from "@/lib/hooks/use-interview-socket";

const PHASE_ORDER = [
  "brand_mapping",
  "product_truths",
  "customer_reality",
  "policy_edge_cases",
  "trust_signals",
] as const;

const PHASE_LABEL: Record<string, string> = {
  brand_mapping: "Brand Mapping",
  product_truths: "Product Truths",
  customer_reality: "Customer Reality",
  policy_edge_cases: "Policy Edge Cases",
  trust_signals: "Trust Signals",
};

interface MicState {
  supported: boolean;
  listening: boolean;
  interimText: string;
  start: () => void;
  stop: () => void;
}

function useWebSpeech(onFinal: (text: string) => void): MicState {
  const recognitionRef = React.useRef<unknown>(null);
  const [supported, setSupported] = React.useState(false);
  const [listening, setListening] = React.useState(false);
  const [interimText, setInterimText] = React.useState("");

  React.useEffect(() => {
    if (typeof window === "undefined") return;
    type SR = new () => {
      continuous: boolean;
      interimResults: boolean;
      lang: string;
      onresult: (e: { results: ArrayLike<{ isFinal: boolean; 0: { transcript: string } }> }) => void;
      onend: () => void;
      start: () => void;
      stop: () => void;
    };
    const Constructor = (window as unknown as { SpeechRecognition?: SR; webkitSpeechRecognition?: SR })
      .SpeechRecognition ?? (window as unknown as { webkitSpeechRecognition?: SR }).webkitSpeechRecognition;
    if (!Constructor) return;
    const rec = new Constructor();
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = "en-US";
    rec.onresult = (event) => {
      let interim = "";
      for (let i = 0; i < event.results.length; i += 1) {
        const r = event.results[i]!;
        if (r.isFinal) {
          const final = r[0].transcript.trim();
          if (final) onFinal(final);
        } else {
          interim += r[0].transcript;
        }
      }
      setInterimText(interim);
    };
    rec.onend = () => setListening(false);
    recognitionRef.current = rec;
    setSupported(true);
  }, [onFinal]);

  function start(): void {
    const rec = recognitionRef.current as { start: () => void } | null;
    if (!rec) return;
    try {
      rec.start();
      setListening(true);
    } catch {
      // already started
    }
  }
  function stop(): void {
    const rec = recognitionRef.current as { stop: () => void } | null;
    rec?.stop();
    setListening(false);
  }

  return { supported, listening, interimText, start, stop };
}

export default function InterviewPage({ params }: { params: { id: string } }): React.ReactElement {
  const { state, start, nextQuestion, advancePhase, sendText } = useInterviewSocket(params.id);
  const [textDraft, setTextDraft] = React.useState("");
  const [graphNodes, setGraphNodes] = React.useState<GraphNode[]>([]);
  const [graphEdges] = React.useState<GraphEdge[]>([]);
  const transcriptEndRef = React.useRef<HTMLDivElement | null>(null);

  // Convert backend "added" stream into ForceGraph nodes (+ pulse fresh).
  React.useEffect(() => {
    if (state.added.length === 0) return;
    setGraphNodes((prev) => {
      const seen = new Set(prev.map((n) => n.id));
      const incoming: GraphNode[] = [];
      for (const a of state.added) {
        if (seen.has(a.id)) continue;
        incoming.push({
          id: a.id,
          type: a.type,
          label: a.label ?? a.id,
          confidence: 0.7,
          fresh: true,
        });
        seen.add(a.id);
      }
      return [...prev.map((n) => ({ ...n, fresh: false })), ...incoming];
    });
  }, [state.added]);

  // Auto-scroll transcript.
  React.useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [state.transcript.length]);

  const mic = useWebSpeech(React.useCallback((text: string) => sendText(text), [sendText]));

  function submitText(): void {
    const text = textDraft.trim();
    if (!text) return;
    sendText(text);
    setTextDraft("");
  }

  const phaseIdx = PHASE_ORDER.indexOf(state.phase as (typeof PHASE_ORDER)[number]);
  const totalNodes = graphNodes.length;
  const totalEdges = graphEdges.length;
  const elapsed = state.progress?.elapsed_minutes ?? 0;

  return (
    <SiteShell>
      <header className="mb-4 flex items-baseline justify-between gap-4">
        <div className="space-y-1">
          <p className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
            /interview/{params.id}
          </p>
          <h1 className="text-2xl font-bold tracking-tight">Live interview</h1>
        </div>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span className="font-mono">
            phase {phaseIdx + 1}/5 - {state.phaseLabel}
          </span>
          <span className="font-mono">{elapsed.toFixed(1)} min elapsed</span>
          <span className="font-mono">{state.progress?.question_count ?? 0} Qs</span>
          <span
            className={
              state.ready
                ? "rounded-full bg-emerald-500/20 px-2 py-0.5 text-emerald-300"
                : "rounded-full bg-amber-500/20 px-2 py-0.5 text-amber-300"
            }
          >
            {state.ready ? "WS open" : "WS reconnecting"}
          </span>
        </div>
      </header>

      <div className="mb-4 flex flex-wrap gap-2">
        <Button onClick={() => start()} disabled={!state.ready}>
          <Play className="mr-2 h-4 w-4" /> Start interview
        </Button>
        <Button onClick={() => nextQuestion()} variant="outline" disabled={!state.ready}>
          <ChevronRight className="mr-2 h-4 w-4" /> Next question
        </Button>
        <Button onClick={() => advancePhase()} variant="outline" disabled={!state.ready}>
          <SkipForward className="mr-2 h-4 w-4" /> Advance phase
        </Button>
        {mic.supported && (
          <Button
            onClick={() => (mic.listening ? mic.stop() : mic.start())}
            variant={mic.listening ? "default" : "outline"}
          >
            <Mic className="mr-2 h-4 w-4" />
            {mic.listening ? "Stop mic" : "Start mic (Web Speech)"}
          </Button>
        )}
      </div>

      <div className="grid grid-cols-12 gap-4">
        {/* Left - transcript */}
        <Card className="col-span-12 border-border/60 lg:col-span-4">
          <CardHeader className="flex flex-row items-center gap-2 space-y-0 pb-2">
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Transcript
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[560px] overflow-y-auto pr-2 text-sm">
              {state.transcript.length === 0 && (
                <p className="text-xs text-muted-foreground">
                  Conversation will appear here in real time. Press Start interview to begin.
                </p>
              )}
              <ul className="space-y-2">
                {state.transcript.map((t, i) => (
                  <li
                    key={i}
                    className={
                      t.speaker === "M"
                        ? "rounded-md border border-border/40 bg-muted/30 p-2"
                        : "rounded-md border border-primary/30 bg-primary/5 p-2"
                    }
                  >
                    <div className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">
                      {t.speaker === "M" ? "merchant" : "interviewer"}
                    </div>
                    <p className="leading-snug">{t.text}</p>
                  </li>
                ))}
              </ul>
              {mic.interimText && (
                <p className="mt-2 italic text-muted-foreground">{mic.interimText}</p>
              )}
              <div ref={transcriptEndRef} />
            </div>
          </CardContent>
        </Card>

        {/* Center - current question + text input */}
        <Card className="col-span-12 border-border/60 lg:col-span-5">
          <CardHeader className="flex flex-row items-center gap-2 space-y-0 pb-2">
            <Mic className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Current question
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {state.question ? (
              <div className="space-y-2 rounded-lg border border-border/60 bg-card/30 p-4">
                <p className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
                  {PHASE_LABEL[state.question.phase] ?? state.question.phase}
                </p>
                <p className="text-lg leading-snug">{state.question.text}</p>
                {state.question.follow_up_if_brief && (
                  <p className="text-xs text-muted-foreground">
                    Follow-up if brief: {state.question.follow_up_if_brief}
                  </p>
                )}
              </div>
            ) : (
              <div className="rounded-lg border border-dashed border-border/40 p-4 text-sm text-muted-foreground">
                Press Start interview to receive the first Socratic question.
              </div>
            )}

            <div>
              <label className="mb-1 block text-xs font-medium text-muted-foreground" htmlFor="text-fallback">
                Text fallback (or speak via Web Speech mic)
              </label>
              <textarea
                id="text-fallback"
                value={textDraft}
                onChange={(e) => setTextDraft(e.target.value)}
                rows={4}
                className="w-full rounded-md border border-border/60 bg-background p-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
                placeholder="Type your answer here, or click Start mic above to speak."
                onKeyDown={(e) => {
                  if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                    e.preventDefault();
                    submitText();
                  }
                }}
              />
              <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
                <span>Cmd/Ctrl + Enter to send</span>
                <Button size="sm" onClick={submitText} disabled={!textDraft.trim()}>
                  Send
                </Button>
              </div>
            </div>

            {state.parseFailed && (
              <p className="rounded-md border border-amber-500/40 bg-amber-500/10 p-2 text-xs text-amber-300">
                Last extraction parse-failed; the segment was flagged for review.
              </p>
            )}
            {state.lastError && (
              <p className="rounded-md border border-destructive/40 bg-destructive/5 p-2 text-xs text-destructive">
                {state.lastError}
              </p>
            )}
          </CardContent>
        </Card>

        {/* Right - mini graph */}
        <Card className="col-span-12 border-border/60 lg:col-span-3">
          <CardHeader className="flex flex-row items-center gap-2 space-y-0 pb-2">
            <Network className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Mini graph
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border border-border/40 bg-background/30">
              <ForceGraph nodes={graphNodes} edges={graphEdges} height={420} cooldownTicks={30} />
            </div>
            <p className="mt-2 font-mono text-[11px] text-muted-foreground">
              nodes: {totalNodes} - edges: {totalEdges}
            </p>
          </CardContent>
        </Card>
      </div>
    </SiteShell>
  );
}
