import { BookOpen } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { SectionHeader } from "@/components/ui/section-header";

type SectionPlaceholderProps = {
  hasData?: boolean;
};

export function ReadingOrderSection({ hasData }: SectionPlaceholderProps) {
  return (
    <section className="space-y-6">
      <SectionHeader
        title="Reading Order"
        description="Prioritized files to inspect first — ranked by usefulness, entry points, and mission relevance."
        badge="Open These Files"
        badgeVariant="outline"
      />

      <Card>
        <CardContent className="py-2">
          {hasData ? (
            <div className="divide-y divide-border-subtle">
              {Array.from({ length: 5 }).map((_, index) => (
                <div key={index} className="flex items-center gap-4 px-2 py-4">
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-border bg-surface-overlay text-xs font-semibold text-muted-foreground">
                    {index + 1}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="font-mono text-sm text-foreground">path/to/file.tsx</p>
                    <p className="mt-1 text-sm text-muted-foreground">
                      Reason and confidence will appear here.
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              icon={<BookOpen className="h-5 w-5" />}
              title="No reading order yet"
              description="Generate an analysis to see AI-recommended files with confidence scores."
              className="py-10"
            />
          )}
        </CardContent>
      </Card>
    </section>
  );
}
