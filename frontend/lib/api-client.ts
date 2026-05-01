/**
 * Typed REST client for the Echomind backend.
 *
 * Reads NEXT_PUBLIC_API_BASE_URL. All endpoints from WINNING_PLAN §5.5 should
 * land here as named methods. For now we expose a generic typed `request()` so
 * the wrapper compiles and pages can call it; named methods are added per
 * day-by-day plan.
 */

import { z, type ZodSchema } from "zod";

const BASE_URL: string = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  public readonly status: number;
  public readonly body: unknown;

  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

export interface RequestOptions<TResponse> {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  path: string;
  body?: unknown;
  query?: Record<string, string | number | boolean | undefined>;
  schema?: ZodSchema<TResponse>;
  signal?: AbortSignal;
  headers?: Record<string, string>;
}

function buildUrl(path: string, query?: RequestOptions<unknown>["query"]): string {
  const url = new URL(path.startsWith("http") ? path : `${BASE_URL}${path}`);
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined) url.searchParams.set(key, String(value));
    }
  }
  return url.toString();
}

export async function request<TResponse>(opts: RequestOptions<TResponse>): Promise<TResponse> {
  const { method = "GET", path, body, query, schema, signal, headers } = opts;
  const res = await fetch(buildUrl(path, query), {
    method,
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
    signal,
    cache: "no-store",
  });

  let parsed: unknown = null;
  const text = await res.text();
  if (text) {
    try {
      parsed = JSON.parse(text);
    } catch {
      parsed = text;
    }
  }

  if (!res.ok) {
    throw new ApiError(`${method} ${path} → ${res.status}`, res.status, parsed);
  }

  if (schema) {
    return schema.parse(parsed);
  }
  return parsed as TResponse;
}

// Generic health-check helper - useful for "is backend up?" indicators.
export const healthSchema = z.object({
  status: z.string(),
});
export type Health = z.infer<typeof healthSchema>;

export const apiClient = {
  baseUrl: BASE_URL,
  request,
  health: (signal?: AbortSignal): Promise<Health> =>
    request({ path: "/health", schema: healthSchema, signal }),
};
