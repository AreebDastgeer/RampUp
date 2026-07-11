import { Brain, GitBranch, Map } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const FEATURES = [
  {
    icon: <Map className="h-5 w-5" />,
    title: "Mission-driven onboarding",
    description:
      "Tell RampUp your role and first task. The AI brief maps repository facts to what you actually need to accomplish.",
  },
  {
    icon: <GitBranch className="h-5 w-5" />,
    title: "Architecture & Dependency Intelligence",
    description:
      "Trace internal imports, detected API routes, and execution flow before you write a single line of code.",
  },
  {
    icon: <Brain className="h-5 w-5" />,
    title: "Repository Intelligence",
    description:
      "Static analysis surfaces entry points, classes, health signals, and the files that matter most — no guesswork.",
  },
] as const;

export function FeatureCards() {
  return (
    <section className="w-full max-w-5xl">
      <div className="mb-8 text-center">
        <h3 className="text-lg font-semibold tracking-tight text-foreground sm:text-xl">
          What RampUp delivers
        </h3>
        <p className="mt-2 text-sm text-muted-foreground">
          Real static analysis first, then AI-powered onboarding tailored to your mission.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {FEATURES.map((feature) => (
          <Card key={feature.title} className="border-border/80 bg-surface-raised/60">
            <CardHeader className="pb-3">
              <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-xl bg-accent-muted text-accent">
                {feature.icon}
              </div>
              <CardTitle className="text-base">{feature.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed text-muted-foreground">
                {feature.description}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}
