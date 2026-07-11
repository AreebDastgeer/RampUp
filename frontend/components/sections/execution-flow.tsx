import { Workflow } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { SectionHeader } from "@/components/ui/section-header";

type SectionPlaceholderProps = {
  hasData?: boolean;
};

export function ExecutionFlowSection({ hasData }: SectionPlaceholderProps) {
  return (
    <section className="space-y-6">
      <SectionHeader
        title="Execution Flow"
        description="Repository-first steps to understand the codebase before implementing your mission."
        badge="Implementation Plan"
        badgeVariant="outline"
      />

      <Card>
        <CardContent className="py-6">
          {hasData ? (
            <ol className="relative space-y-6 border-l border-border pl-8">
              {Array.from({ length: 4 }).map((_, index) => (
                <li key={index} className="relative">
                  <span className="absolute -left-[2.15rem] flex h-7 w-7 items-center justify-center rounded-full border border-accent/30 bg-accent-muted text-xs font-semibold text-accent-foreground">
                    {index + 1}
                  </span>
                  <p className="text-sm leading-relaxed text-muted-foreground">
                    Step {index + 1} placeholder — understand entry points, trace dependencies, then implement.
                  </p>
                </li>
              ))}
            </ol>
          ) : (
            <EmptyState
              icon={<Workflow className="h-5 w-5" />}
              title="No execution flow yet"
              description="Your step-by-step contribution plan will appear here after analysis."
            />
          )}
        </CardContent>
      </Card>
    </section>
  );
}
