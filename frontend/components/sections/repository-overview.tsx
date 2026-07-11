import { Boxes, FileCode2, FolderTree, GitBranch } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { SectionHeader } from "@/components/ui/section-header";
import { Skeleton } from "@/components/ui/skeleton";

type SectionPlaceholderProps = {
  hasData?: boolean;
  loading?: boolean;
};

export function RepositoryOverviewSection({ hasData, loading }: SectionPlaceholderProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-7 w-56" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <section className="space-y-6">
      <SectionHeader
        title="Repository Overview"
        description="High-level snapshot of the cloned repository — name, size, technologies, and key files."
        badge={hasData ? "Live data" : "Awaiting analysis"}
        badgeVariant={hasData ? "success" : "outline"}
      />

      {hasData ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { label: "Repository", value: "—", icon: <GitBranch className="h-4 w-4" /> },
            { label: "Files", value: "—", icon: <FileCode2 className="h-4 w-4" /> },
            { label: "Directories", value: "—", icon: <FolderTree className="h-4 w-4" /> },
            { label: "Technologies", value: "—", icon: <Boxes className="h-4 w-4" /> },
          ].map((stat) => (
            <Card key={stat.label}>
              <CardContent className="flex items-start justify-between pt-5">
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                    {stat.label}
                  </p>
                  <p className="mt-2 text-2xl font-semibold tracking-tight">{stat.value}</p>
                </div>
                <div className="rounded-lg border border-border bg-surface-overlay p-2 text-muted-foreground">
                  {stat.icon}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={<GitBranch className="h-5 w-5" />}
          title="No repository analyzed yet"
          description="Submit a GitHub URL to populate the repository overview with factual metadata from static analysis."
        />
      )}

      <Card>
        <CardHeader>
          <CardTitle>Important Files & README</CardTitle>
        </CardHeader>
        <CardContent>
          <EmptyState
            title="Visualization coming soon"
            description="This panel will show usefulness-ranked files, entry points, and README excerpts."
            className="border-none bg-transparent py-8"
          />
        </CardContent>
      </Card>
    </section>
  );
}
