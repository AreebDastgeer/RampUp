"use client";

import { Network, Route, Workflow } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { SectionHeader } from "@/components/ui/section-header";
import { useAnalysis } from "@/lib/store/analysis-context";

function methodVariant(method: string): "success" | "accent" | "warning" | "outline" {
  const primary = method.split(",")[0]?.trim().toUpperCase();
  if (primary === "GET") return "success";
  if (primary === "POST") return "accent";
  if (primary === "DELETE" || primary === "PUT" || primary === "PATCH") return "warning";
  return "outline";
}

export function ArchitecturePageContent() {
  const { analysis } = useAnalysis();
  const repo = analysis!.repository;
  const brief = analysis!.rampup_brief;

  const executionSteps =
    brief?.repository_navigation?.execution_flow ??
    brief?.architecture_walkthrough?.map((s) => s.description) ??
    [];

  return (
    <section className="space-y-8">
      <SectionHeader
        title="Architecture"
        description="Execution flow, internal dependencies, and detected API routes from static analysis."
        badge="Static analysis"
        badgeVariant="accent"
      />

      <div>
        <SectionHeader
          title="Execution Flow"
          description="Repository-first steps to understand the codebase before implementing your mission."
          badge="Implementation Plan"
          badgeVariant="outline"
          className="mb-4"
        />
        <Card>
          <CardContent className="py-6">
            {executionSteps.length > 0 ? (
              <ol className="relative space-y-6 border-l border-border pl-8">
                {executionSteps.map((step, index) => (
                  <li key={index} className="relative">
                    <span className="absolute -left-[2.15rem] flex h-7 w-7 items-center justify-center rounded-full border border-accent/30 bg-accent-muted text-xs font-semibold text-accent-foreground">
                      {index + 1}
                    </span>
                    <p className="text-sm leading-relaxed text-foreground">{step}</p>
                  </li>
                ))}
              </ol>
            ) : (
              <EmptyState
                icon={<Workflow className="h-5 w-5" />}
                title="No execution flow available"
                description="The AI brief did not include execution flow steps. Check the Mission page for implementation guidance."
              />
            )}
          </CardContent>
        </Card>
      </div>

      <div>
        <SectionHeader
          title="Dependency Explorer"
          description="Internal import relationships detected by static analysis."
          badge={`${repo.dependency_map.length} edges`}
          badgeVariant="accent"
          className="mb-4"
        />
        <div className="grid gap-4 lg:grid-cols-5">
          <Card className="lg:col-span-3">
            <CardHeader>
              <CardTitle>Import Relationships</CardTitle>
            </CardHeader>
            <CardContent>
              {repo.dependency_map.length > 0 ? (
                <div className="max-h-80 space-y-2 overflow-y-auto">
                  {repo.dependency_map.map((edge, index) => (
                    <div
                      key={`${edge.source}-${edge.target}-${index}`}
                      className="flex items-center gap-2 rounded-lg border border-border bg-surface-overlay px-3 py-2 font-mono text-xs"
                    >
                      <span className="truncate text-foreground">{edge.source}</span>
                      <span className="shrink-0 text-muted-foreground">→</span>
                      <span className="truncate text-accent-foreground">{edge.target}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState
                  icon={<Network className="h-5 w-5" />}
                  title="No dependency edges detected"
                  description="Internal import relationships will appear here when detected."
                  className="min-h-[200px] justify-center"
                />
              )}
            </CardContent>
          </Card>

          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Import Hubs</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {repo.code_analysis.files_with_most_imports.length > 0 ? (
                  repo.code_analysis.files_with_most_imports.map((file) => (
                    <div
                      key={file.path}
                      className="rounded-lg border border-border bg-surface-overlay px-3 py-2.5"
                    >
                      <p className="font-mono text-xs text-foreground">{file.path}</p>
                      <p className="mt-1 text-xs text-muted-foreground">
                        {file.import_count} imports
                      </p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground">
                    Files with the most imports will rank here.
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {brief?.repository_navigation?.important_dependencies &&
        brief.repository_navigation.important_dependencies.length > 0 ? (
          <Card className="mt-4">
            <CardHeader>
              <CardTitle>Important Dependencies</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {brief.repository_navigation.important_dependencies.map((dep) => (
                  <Badge key={dep} variant="outline">
                    {dep}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        ) : null}
      </div>

      <div>
        <SectionHeader
          title="API Explorer"
          description="HTTP routes parsed from FastAPI, Flask, and Express decorators in source code."
          badge={`${repo.api_endpoints.length} routes`}
          badgeVariant="accent"
          className="mb-4"
        />
        <Card>
          <CardContent className="p-0">
            {repo.api_endpoints.length > 0 ? (
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
                    {repo.api_endpoints.map((endpoint, index) => (
                      <tr
                        key={`${endpoint.method}-${endpoint.path}-${endpoint.file}-${index}`}
                        className="border-b border-border-subtle last:border-0"
                      >
                        <td className="px-5 py-3">
                          {endpoint.method.split(",").map((m) => (
                            <Badge key={m.trim()} variant={methodVariant(m.trim())} className="mr-1">
                              {m.trim()}
                            </Badge>
                          ))}
                        </td>
                        <td className="px-5 py-3 font-mono text-foreground">{endpoint.path}</td>
                        <td className="px-5 py-3 font-mono text-muted-foreground">
                          {endpoint.file}:{endpoint.line}
                        </td>
                        <td className="px-5 py-3 text-muted-foreground">
                          {endpoint.framework || "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <EmptyState
                icon={<Route className="h-5 w-5" />}
                title="No API routes detected"
                description="No HTTP routes were found in framework decorators or route definitions."
                className="py-12"
              />
            )}
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
