import { Check, CircleDashed, Plug, ShoppingBag, UserCircle } from "lucide-react";

import { SiteShell } from "@/components/site-shell";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const STEPS: ReadonlyArray<{
  n: number;
  title: string;
  description: string;
  icon: typeof Check;
}> = [
  {
    n: 1,
    title: "Sign in with Google",
    description: "Firebase Auth - one click, no passwords.",
    icon: UserCircle,
  },
  {
    n: 2,
    title: "Connect Shopify",
    description: "Real OAuth → callback → admin token stored in Firestore.",
    icon: Plug,
  },
  {
    n: 3,
    title: "Live ingest",
    description:
      "Watch products, policies, FAQs, and reviews stream into the graph in real time.",
    icon: ShoppingBag,
  },
  {
    n: 4,
    title: "Start the audit",
    description: "≈25 min: 20 min Socratic interview + 5 min agent simulation.",
    icon: CircleDashed,
  },
];

export default function OnboardPage(): JSX.Element {
  return (
    <SiteShell>
      <div className="mx-auto max-w-3xl space-y-8">
        <header className="space-y-2">
          <p className="font-mono text-xs uppercase tracking-wider text-muted-foreground">
            /onboard
          </p>
          <h1 className="text-3xl font-bold tracking-tight">Connect your Shopify store</h1>
          <p className="text-muted-foreground">
            4-step wizard placeholder - coming Day 2. Real Shopify OAuth + live catalog crawl.
          </p>
        </header>
        <ol className="space-y-3">
          {STEPS.map((step) => {
            const Icon = step.icon;
            return (
              <li key={step.n}>
                <Card className="border-border/60">
                  <CardHeader className="flex flex-row items-start gap-4 space-y-0">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-muted">
                      <Icon className="h-5 w-5 text-muted-foreground" aria-hidden />
                    </div>
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs text-muted-foreground">
                          STEP {step.n}
                        </span>
                      </div>
                      <CardTitle className="text-lg">{step.title}</CardTitle>
                      <CardDescription>{step.description}</CardDescription>
                    </div>
                  </CardHeader>
                </Card>
              </li>
            );
          })}
        </ol>
        <div className="rounded-lg border border-dashed border-border/60 bg-card/40 p-6 text-sm text-muted-foreground">
          <p className="font-mono text-xs uppercase tracking-wider">Status</p>
          <p className="mt-1">Onboard wizard - coming Day 2.</p>
        </div>
      </div>
    </SiteShell>
  );
}
