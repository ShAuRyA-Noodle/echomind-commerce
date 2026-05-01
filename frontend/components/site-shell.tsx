import * as React from "react";
import Link from "next/link";

import { cn } from "@/lib/utils";

const NAV_LINKS: ReadonlyArray<{ href: string; label: string }> = [
  { href: "/onboard", label: "Onboard" },
  { href: "/interview/demo", label: "Interview" },
  { href: "/audit/demo", label: "Audit" },
  { href: "/simulate/demo", label: "Simulate" },
  { href: "/graph/demo", label: "Graph" },
  { href: "/policies/returns", label: "Policies" },
  { href: "/replay/demo", label: "Replay" },
];

export function SiteShell({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}): React.ReactElement {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-30 border-b border-border/60 bg-background/80 backdrop-blur">
        <div className="mx-auto flex h-14 w-full max-w-screen-2xl items-center justify-between px-6">
          <Link href="/" className="flex items-center gap-2">
            <span className="inline-block h-2.5 w-2.5 rounded-full bg-[var(--node-fix-suggestion)]" />
            <span className="font-mono text-sm font-semibold tracking-tight">
              echomind / commerce
            </span>
          </Link>
          <nav className="hidden items-center gap-5 text-xs text-muted-foreground md:flex">
            {NAV_LINKS.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                className="transition-colors hover:text-foreground"
              >
                {l.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <main className={cn("mx-auto w-full max-w-screen-2xl flex-1 px-6 py-8", className)}>
        {children}
      </main>
      <footer className="border-t border-border/60 px-6 py-4 text-xs text-muted-foreground">
        <div className="mx-auto flex w-full max-w-screen-2xl items-center justify-between">
          <span className="font-mono">echomind-commerce · scaffold</span>
          <span className="font-mono">Track 5 · AI Representation Optimizer</span>
        </div>
      </footer>
    </div>
  );
}
