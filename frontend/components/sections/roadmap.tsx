import { GitBranch } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { SectionHeader } from "@/components/ui/section-header";

type SectionPlaceholderProps = {
  hasData?: boolean;
};

export function RoadmapSection({ hasData }: SectionPlaceholderProps) {
  return (
    <section className="space-y-6">
      <SectionHeader
        title="Roadmap"
        description="Suggested implementation sequence from the AI brief — repository-first, then mission-specific."
        badge="Implementation Plan"
        badgeVariant="outline"
      />

      <Card>
        <CardContent className="py-6">
          {hasData ? (
            <div className="grid gap-4 md:grid-cols-3">
              {["Understand", "Explore", "Implement"].map((phase, index) => (
                <div
                  key={phase}
                  className="rounded-xl border border-border bg-surface-overlay p-4"
                >
                  <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                    Phase {index + 1}
                  </p>
                  <p className="mt-2 text-sm font-semibold text-foreground">{phase}</p>
                  <p className="mt-2 text-sm text-muted-foreground">
                    Roadmap steps will be grouped by phase here.
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              icon={<GitBranch className="h-5 w-5" />}
              title="No roadmap generated"
              description="The AI implementation plan will render as a phased roadmap after analysis."
            />
          )}
        </CardContent>
      </Card>
    </section>
  );
}
