import { Route } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { SectionHeader } from "@/components/ui/section-header";

type SectionPlaceholderProps = {
  hasData?: boolean;
};

export function ApiExplorerSection({ hasData }: SectionPlaceholderProps) {
  return (
    <section className="space-y-6">
      <SectionHeader
        title="API Explorer"
        description="HTTP routes parsed from FastAPI, Flask, and Express decorators in source code."
        badge="Parsed routes"
        badgeVariant="accent"
      />

      <Card>
        <CardContent className="p-0">
          {hasData ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-border text-xs uppercase tracking-wide text-muted-foreground">
                    <th className="px-5 py-3 font-medium">Method</th>
                    <th className="px-5 py-3 font-medium">Path</th>
                    <th className="px-5 py-3 font-medium">File</th>
                    <th className="px-5 py-3 font-medium">Framework</th>
                  </tr>
                </thead>
                <tbody>
                  {Array.from({ length: 4 }).map((_, i) => (
                    <tr key={i} className="border-b border-border-subtle last:border-0">
                      <td className="px-5 py-3">
                        <Badge variant="success">GET</Badge>
                      </td>
                      <td className="px-5 py-3 font-mono text-foreground">/api/endpoint</td>
                      <td className="px-5 py-3 font-mono text-muted-foreground">main.py:26</td>
                      <td className="px-5 py-3 text-muted-foreground">FastAPI</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState
              icon={<Route className="h-5 w-5" />}
              title="No API routes detected"
              description="Submit a backend repository to extract routes from framework decorators."
              className="py-12"
            />
          )}
        </CardContent>
      </Card>
    </section>
  );
}
