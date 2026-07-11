import { Activity, CheckCircle2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { SectionHeader } from "@/components/ui/section-header";

type SectionPlaceholderProps = {
  hasData?: boolean;
};

const HEALTH_SIGNALS = [
  "README present",
  "License present",
  "Tests detected",
  "Docker detected",
  "CI workflow detected",
  "GitHub Actions detected",
  "Env example detected",
  "Package manager detected",
] as const;

export function RepositoryHealthSection({ hasData }: SectionPlaceholderProps) {
  return (
    <section className="space-y-6">
      <SectionHeader
        title="Repository Health"
        description="Factual health signals computed automatically from the filesystem — not inferred by AI."
        badge="Automated"
        badgeVariant="success"
      />

      {hasData ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {HEALTH_SIGNALS.map((signal) => (
            <Card key={signal}>
              <CardContent className="flex items-center gap-3 pt-5">
                <div className="rounded-lg border border-border bg-surface-overlay p-2 text-muted-foreground">
                  <Activity className="h-4 w-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-foreground">{signal}</p>
                  <p className="text-xs text-muted-foreground">Pending wiring</p>
                </div>
                <CheckCircle2 className="h-4 w-4 shrink-0 text-muted" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={<Activity className="h-5 w-5" />}
          title="Health check not run"
          description="Repository health flags will populate after the first analysis."
        />
      )}
    </section>
  );
}
