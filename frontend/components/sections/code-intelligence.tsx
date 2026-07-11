import { Brain, Code2, FunctionSquare, Layers } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { SectionHeader } from "@/components/ui/section-header";

type SectionPlaceholderProps = {
  hasData?: boolean;
};

export function CodeIntelligenceSection({ hasData }: SectionPlaceholderProps) {
  return (
    <section className="space-y-6">
      <SectionHeader
        title="Code Intelligence"
        description="AST-derived facts — classes, functions, largest files, and import frequency."
        badge="Python AST"
        badgeVariant="accent"
      />

      <div className="grid gap-4 md:grid-cols-2">
        {[
          { title: "Classes", icon: <Layers className="h-4 w-4" />, count: "—" },
          { title: "Functions", icon: <FunctionSquare className="h-4 w-4" />, count: "—" },
          { title: "Largest Files", icon: <Code2 className="h-4 w-4" />, count: "—" },
          { title: "Import Hubs", icon: <Brain className="h-4 w-4" />, count: "—" },
        ].map((panel) => (
          <Card key={panel.title}>
            <CardHeader className="flex-row items-center justify-between space-y-0">
              <CardTitle className="flex items-center gap-2">
                {panel.icon}
                {panel.title}
              </CardTitle>
              <span className="text-sm font-semibold text-muted-foreground">{panel.count}</span>
            </CardHeader>
            <CardContent>
              <EmptyState
                title={hasData ? "Data available" : "No analysis yet"}
                description={`${panel.title} panel — visualization wiring comes next.`}
                className="border-none bg-transparent py-4"
              />
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}
