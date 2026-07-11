import { Network } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { SectionHeader } from "@/components/ui/section-header";

type SectionPlaceholderProps = {
  hasData?: boolean;
};

export function DependencyExplorerSection({ hasData }: SectionPlaceholderProps) {
  return (
    <section className="space-y-6">
      <SectionHeader
        title="Dependency Explorer"
        description="Internal import relationships detected by static analysis — which files depend on which."
        badge="AST + regex"
        badgeVariant="accent"
      />

      <div className="grid gap-4 lg:grid-cols-5">
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Import Graph</CardTitle>
          </CardHeader>
          <CardContent>
            <EmptyState
              icon={<Network className="h-5 w-5" />}
              title="Graph visualization coming soon"
              description={
                hasData
                  ? "Dependency edges are available from the API — interactive graph rendering is next."
                  : "Analyze a repository to build the internal dependency map."
              }
              className="min-h-[280px] justify-center"
            />
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Import Hubs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {hasData
                ? Array.from({ length: 4 }).map((_, i) => (
                    <div
                      key={i}
                      className="rounded-lg border border-border bg-surface-overlay px-3 py-2.5"
                    >
                      <p className="font-mono text-xs text-foreground">module/file.py</p>
                      <p className="mt-1 text-xs text-muted-foreground">— imports</p>
                    </div>
                  ))
                : (
                    <p className="text-sm text-muted-foreground">
                      Files with the most imports will rank here.
                    </p>
                  )}
            </div>
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
