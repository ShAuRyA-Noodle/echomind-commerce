/**
 * Echomind Commerce - typed WebSocket client.
 *
 * The interview view (`/interview/[id]`) and the simulator view
 * (`/simulate/[runId]`) both consume bidirectional WS streams from the
 * FastAPI backend. This module is the typed wrapper around the browser
 * `WebSocket` API used by both.
 *
 * Per WINNING_PLAN §5.5 the contract is:
 *
 *   /api/interview/ws/{session_id}
 *     out: interim_transcript | final_transcript | question | extraction
 *        | phase_change | graph_update | progress | error
 *     in:  audio_chunk | text_input | control
 *
 *   /api/simulate/ws/{run_id}
 *     out: agent_token | agent_done | run_progress | error
 *     in:  control (start | pause | stop)
 *
 * This wrapper:
 *   - reconnects with exponential backoff (1s → 2s → 4s → 8s, capped at 30s)
 *   - dedupes identical events fired within a 50ms window (LLM streaming
 *     can spam duplicates on socket-flap)
 *   - exposes a typed `send()` that JSON-encodes the payload
 *   - exposes a typed `subscribe(type, handler)` that filters by `type` field
 *   - cleans up listeners on `close()`
 *
 * It is small on purpose. Pages should consume it via thin React hooks
 * (`useInterviewSocket`, `useSimulateSocket`) rather than reaching directly.
 */

const WS_BASE_URL: string =
  process.env.NEXT_PUBLIC_WS_BASE_URL ?? "ws://localhost:8000";

const RECONNECT_BACKOFF_MS = [1_000, 2_000, 4_000, 8_000, 16_000, 30_000] as const;

export interface BackendEvent {
  type: string;
  [key: string]: unknown;
}

export type EventHandler<T extends BackendEvent = BackendEvent> = (event: T) => void;

export interface WsClientOptions {
  /** Path beneath `WS_BASE_URL`, e.g. `/api/interview/ws/abc123`. */
  path: string;
  /** Called once the socket OPENs (after each reconnect). */
  onOpen?: () => void;
  /** Called when the socket transitions to CLOSED with no further reconnects. */
  onClose?: (event: CloseEvent) => void;
  /** Called for any unhandled error; default logs to console. */
  onError?: (event: Event) => void;
  /** If set, abort reconnection after this many failed attempts. Default 6. */
  maxReconnectAttempts?: number;
  /** Token for `?token=…` if the backend wants auth on the WS query string. */
  authToken?: string;
}

export interface WsClient {
  readonly url: string;
  readonly readyState: () => number;
  send(payload: BackendEvent | Record<string, unknown>): void;
  subscribe<T extends BackendEvent = BackendEvent>(
    type: string,
    handler: EventHandler<T>,
  ): () => void;
  close(): void;
}

interface DedupeEntry {
  signature: string;
  ts: number;
}

function buildUrl(path: string, authToken?: string): string {
  const base = WS_BASE_URL.replace(/\/$/, "");
  const sep = path.startsWith("/") ? "" : "/";
  const url = `${base}${sep}${path}`;
  if (!authToken) return url;
  const u = new URL(url);
  u.searchParams.set("token", authToken);
  return u.toString();
}

/**
 * Create a typed WebSocket client with auto-reconnect and event dedupe.
 *
 * Returns immediately; the underlying socket connects asynchronously.
 * Subscribe before sending if you need to capture early events.
 */
export function createWsClient(opts: WsClientOptions): WsClient {
  const url = buildUrl(opts.path, opts.authToken);
  const maxAttempts = opts.maxReconnectAttempts ?? 6;

  let socket: WebSocket | null = null;
  let reconnectAttempt = 0;
  let manuallyClosed = false;
  let reconnectTimer: number | null = null;
  const handlers = new Map<string, Set<EventHandler>>();
  const dedupe: DedupeEntry[] = [];

  function dedupeShouldDrop(serialized: string): boolean {
    const now = Date.now();
    // GC entries older than 100ms.
    while (dedupe.length && now - dedupe[0]!.ts > 100) {
      dedupe.shift();
    }
    if (dedupe.find((e) => e.signature === serialized && now - e.ts < 50)) {
      return true;
    }
    dedupe.push({ signature: serialized, ts: now });
    return false;
  }

  function dispatch(event: BackendEvent): void {
    const set = handlers.get(event.type);
    if (!set) return;
    for (const h of Array.from(set)) {
      try {
        h(event);
      } catch (err) {
        console.error("[ws-client] handler threw", err);
      }
    }
  }

  function scheduleReconnect(): void {
    if (manuallyClosed) return;
    if (reconnectAttempt >= maxAttempts) {
      console.warn(`[ws-client] giving up after ${maxAttempts} attempts: ${url}`);
      return;
    }
    const delayIdx = Math.min(reconnectAttempt, RECONNECT_BACKOFF_MS.length - 1);
    const delay = RECONNECT_BACKOFF_MS[delayIdx]!;
    reconnectAttempt += 1;
    reconnectTimer = window.setTimeout(connect, delay);
  }

  function connect(): void {
    if (manuallyClosed) return;
    if (typeof window === "undefined") return; // SSR guard

    try {
      socket = new WebSocket(url);
    } catch (err) {
      console.error("[ws-client] construct failed", err);
      scheduleReconnect();
      return;
    }

    socket.addEventListener("open", () => {
      reconnectAttempt = 0;
      opts.onOpen?.();
    });

    socket.addEventListener("message", (msg: MessageEvent) => {
      const raw = typeof msg.data === "string" ? msg.data : "";
      if (!raw) return;
      if (dedupeShouldDrop(raw)) return;
      let parsed: unknown;
      try {
        parsed = JSON.parse(raw);
      } catch {
        // Non-JSON frames are ignored; backend always sends JSON.
        return;
      }
      if (
        typeof parsed === "object" &&
        parsed !== null &&
        "type" in parsed &&
        typeof (parsed as Record<string, unknown>).type === "string"
      ) {
        dispatch(parsed as BackendEvent);
      }
    });

    socket.addEventListener("error", (event) => {
      if (opts.onError) opts.onError(event);
      else console.error("[ws-client] error", event);
    });

    socket.addEventListener("close", (event: CloseEvent) => {
      if (manuallyClosed) {
        opts.onClose?.(event);
        return;
      }
      scheduleReconnect();
    });
  }

  // Kick off async.
  connect();

  return {
    url,
    readyState: () => socket?.readyState ?? WebSocket.CLOSED,
    send: (payload) => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(payload));
      } else {
        console.warn("[ws-client] send() called while not OPEN; dropping", payload);
      }
    },
    subscribe<T extends BackendEvent = BackendEvent>(
      type: string,
      handler: EventHandler<T>,
    ): () => void {
      let set = handlers.get(type);
      if (!set) {
        set = new Set();
        handlers.set(type, set);
      }
      set.add(handler as EventHandler);
      return () => {
        const s = handlers.get(type);
        if (!s) return;
        s.delete(handler as EventHandler);
        if (s.size === 0) handlers.delete(type);
      };
    },
    close: () => {
      manuallyClosed = true;
      if (reconnectTimer !== null) {
        window.clearTimeout(reconnectTimer);
        reconnectTimer = null;
      }
      if (socket) {
        try {
          socket.close(1000, "client_manual_close");
        } catch {
          /* ignore */
        }
        socket = null;
      }
      handlers.clear();
    },
  };
}

// ---------------------------------------------------------------------------
// Convenience helpers - typed paths
// ---------------------------------------------------------------------------

export function interviewWsPath(sessionId: string): string {
  return `/api/interview/ws/${encodeURIComponent(sessionId)}`;
}

export function simulateWsPath(runId: string): string {
  return `/api/simulate/ws/${encodeURIComponent(runId)}`;
}
