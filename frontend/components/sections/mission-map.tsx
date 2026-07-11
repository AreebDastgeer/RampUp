import { Map } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { SectionHeader } from "@/components/ui/section-header";

type SectionPlaceholderProps = {
  hasData?: boolean;
};

export function MissionMapSection({ hasData }: SectionPlaceholderProps) {
  return (
    <section className="space-y-6">
      <SectionHeader
        title="Mission Map"
        description="Mission-aligned focus areas derived from your role, task, and detected repository structure."
        badge="AI-powered"
        badgeVariant="accent"
      />

      <div className="grid gap-4 lg:grid-cols-3">
        {["Concepts", "Focus Files", "Mission Alignment"].map((panel) => (
          <Card key={panel}>
            <CardHeader>
              <CardTitle>{panel}</CardTitle>
            </CardHeader>
            <CardContent>
              <EmptyState
                icon={<Map className="h-5 w-5" />}
                title={hasData ? "Processing mission context" : "Awaiting mission"}
                description={`The ${panel.toLowerCase()} visualization will map your mission to repository facts.`}
                className="border-none bg-transparent py-6"
              />
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}
