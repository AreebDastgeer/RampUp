"use client";

import { Brain, Code2, FunctionSquare, Layers } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SectionHeader } from "@/components/ui/section-header";
import { useAnalysis } from "@/lib/store/analysis-context";

export function IntelligencePageContent() {
  const { analysis } = useAnalysis();
  const code = analysis!.repository.code_analysis;
  const imports = analysis!.repository.imports;

  return (
    <section className="space-y-6">
      <SectionHeader
        title="Code Intelligence"
        description="AST-derived facts — classes, functions, largest files, and import frequency."
        badge={`${code.python_files_analyzed} Python · ${code.javascript_files_analyzed} JS`}
        badgeVariant="accent"
      />

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="flex-row items-center justify-between space-y-0">
            <CardTitle className="flex items-center gap-2">
              <Layers className="h-4 w-4" />
              Classes
            </CardTitle>
            <span className="text-sm font-semibold text-muted-foreground">
              {code.classes.length}
            </span>
          </CardHeader>
          <CardContent>
            {code.classes.length > 0 ? (
              <div className="max-h-64 space-y-2 overflow-y-auto">
                {code.classes.map((cls) => (
                  <div
                    key={`${cls.file}-${cls.line}-${cls.name}`}
                    className="flex items-center justify-between rounded-lg border border-border bg-surface-overlay px-3 py-2"
                  >
                    <span className="font-mono text-xs text-foreground">{cls.name}</span>
                    <span className="font-mono text-xs text-muted-foreground">
                      {cls.file}:{cls.line}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No Python classes detected.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex-row items-center justify-between space-y-0">
            <CardTitle className="flex items-center gap-2">
              <FunctionSquare className="h-4 w-4" />
              Functions
            </CardTitle>
            <span className="text-sm font-semibold text-muted-foreground">
              {code.functions.length}
            </span>
          </CardHeader>
          <CardContent>
            {code.functions.length > 0 ? (
              <div className="max-h-64 space-y-2 overflow-y-auto">
                {code.functions.map((fn) => (
                  <div
                    key={`${fn.file}-${fn.line}-${fn.name}`}
                    className="flex items-center justify-between rounded-lg border border-border bg-surface-overlay px-3 py-2"
                  >
                    <span className="font-mono text-xs text-foreground">{fn.name}</span>
                    <span className="font-mono text-xs text-muted-foreground">
                      {fn.file}:{fn.line}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No top-level functions detected.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex-row items-center justify-between space-y-0">
            <CardTitle className="flex items-center gap-2">
              <Code2 className="h-4 w-4" />
              Largest Files
            </CardTitle>
            <span className="text-sm font-semibold text-muted-foreground">
              {code.largest_files.length}
            </span>
          </CardHeader>
          <CardContent>
            {code.largest_files.length > 0 ? (
              <div className="space-y-2">
                {code.largest_files.map((file) => (
                  <div
                    key={file.path}
                    className="flex items-center justify-between rounded-lg border border-border bg-surface-overlay px-3 py-2"
                  >
                    <span className="truncate font-mono text-xs text-foreground">{file.path}</span>
                    <div className="flex shrink-0 gap-2">
                      <Badge variant="outline">{file.lines} lines</Badge>
                      <Badge variant="outline">{Math.round(file.bytes / 1024)} KB</Badge>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No file size data available.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex-row items-center justify-between space-y-0">
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              Import Hubs
            </CardTitle>
            <span className="text-sm font-semibold text-muted-foreground">
              {code.files_with_most_imports.length}
            </span>
          </CardHeader>
          <CardContent>
            {code.files_with_most_imports.length > 0 ? (
              <div className="space-y-2">
                {code.files_with_most_imports.map((file) => (
                  <div
                    key={file.path}
                    className="rounded-lg border border-border bg-surface-overlay px-3 py-2"
                  >
                    <p className="font-mono text-xs text-foreground">{file.path}</p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {file.import_count} imports
                      {file.internal_count !== undefined
                        ? ` · ${file.internal_count} internal · ${file.external_count} external`
                        : ""}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No import hub data available.</p>
            )}
          </CardContent>
        </Card>
      </div>

      {imports.frequent_packages.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Dependency Insights — Frequent Packages</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
              {imports.frequent_packages.map((pkg) => (
                <div
                  key={pkg.package}
                  className="flex items-center justify-between rounded-lg border border-border bg-surface-overlay px-3 py-2"
                >
                  <span className="font-mono text-xs text-foreground">{pkg.package}</span>
                  <Badge variant="accent">{pkg.count}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : null}
    </section>
  );
}
