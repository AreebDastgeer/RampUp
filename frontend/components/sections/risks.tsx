import { AlertTriangle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { SectionHeader } from "@/components/ui/section-header";

type SectionPlaceholderProps = {
  hasData?: boolean;
};

export function RisksSection({ hasData }: SectionPlaceholderProps) {
  return (
    <section className="space-y-6">
      <SectionHeader
        title="Risks"
        description="Evidence-based onboarding risks — only surfaced when supported by repository analysis."
        badge="Potential Risks"
        badgeVariant="warning"
      />

      <Card>
        <CardContent className="py-2">
          {hasData ? (
            <div className="divide-y divide-border-subtle">
              {Array.from({ length: 3 }).map((_, index) => (
                <div key={index} className="flex gap-4 px-2 py-4">
                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-warning/30 bg-warning/10 text-warning">
                    <AlertTriangle className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-foreground">Risk placeholder {index + 1}</p>
                    <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
                      Risk description tied to repository evidence will appear here.
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              icon={<AlertTriangle className="h-5 w-5" />}
              title="No risks identified yet"
              description="Risks are generated from repository evidence after analysis completes."
              className="py-10"
            />
          )}
        </CardContent>
      </Card>
    </section>
  );
}
