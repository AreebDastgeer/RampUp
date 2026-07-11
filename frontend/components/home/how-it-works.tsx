import { Fragment } from "react";
import { ArrowRight, GitBranch, Sparkles, Workflow } from "lucide-react";

const STEPS = [
  {
    icon: <GitBranch className="h-5 w-5" />,
    label: "GitHub Repository",
    description: "Provide a public repo URL, your role, and your first mission.",
  },
  {
    icon: <Workflow className="h-5 w-5" />,
    label: "Repository Analysis",
    description: "RampUp clones and analyzes structure, imports, routes, and health signals.",
  },
  {
    icon: <Sparkles className="h-5 w-5" />,
    label: "Personalized Ramp-Up",
    description: "Get a mission-aligned brief with reading order, roadmap, and risks.",
  },
] as const;

export function HowItWorks() {
  return (
    <section className="w-full max-w-4xl">
      <div className="mb-8 text-center">
        <h3 className="text-lg font-semibold tracking-tight text-foreground sm:text-xl">
          How It Works
        </h3>
        <p className="mt-2 text-sm text-muted-foreground">
          From repository URL to actionable onboarding in three steps.
        </p>
      </div>

      <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center sm:items-center">
  {STEPS.map((step, index) => (
    <Fragment key={step.label}>
      <div className="flex w-full max-w-[180px] flex-col items-center text-center">
        <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl border border-border bg-surface-overlay text-accent">
          {step.icon}
        </div>

        <p className="text-sm font-semibold text-foreground">
          {step.label}
        </p>

        <p className="mt-1.5 text-xs leading-relaxed text-muted-foreground">
          {step.description}
        </p>
      </div>

      {index < STEPS.length - 1 && (
        <ArrowRight className="hidden sm:block h-5 w-5 text-muted-foreground mx-2 self-center" />
      )}
    </Fragment>
  ))}
</div>
    </section>
  );
}
