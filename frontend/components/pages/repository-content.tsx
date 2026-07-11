"use client";

import { Boxes, FileCode2, FolderTree, GitBranch, Play, FileText } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SectionHeader } from "@/components/ui/section-header";
import { useAnalysis } from "@/lib/store/analysis-context";

export function RepositoryPageContent() {
  const { analysis } = useAnalysis();
  const repo = analysis!.repository;

  return (
    <section className="space-y-6">
      <SectionHeader
        title="Repository Overview"
        description="High-level snapshot of the cloned repository — name, size, technologies, and key files."
        badge="Live data"
        badgeVariant="success"
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: "Repository", value: repo.name, icon: <GitBranch className="h-4 w-4" /> },
          { label: "Files", value: repo.files.toLocaleString(), icon: <FileCode2 className="h-4 w-4" /> },
          {
            label: "Directories",
            value: repo.directories.toLocaleString(),
            icon: <FolderTree className="h-4 w-4" />,
          },
          {
            label: "Technologies",
            value: repo.technologies.length.toString(),
            icon: <Boxes className="h-4 w-4" />,
          },
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

      {repo.project_purpose ? (
        <Card>
          <CardHeader>
            <CardTitle>Project Purpose</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed text-muted-foreground">{repo.project_purpose}</p>
          </CardContent>
        </Card>
      ) : null}

      {repo.technologies.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Technologies</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {repo.technologies.map((tech) => (
                <Badge key={tech} variant="outline">
                  {tech}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : null}

      {repo.top_level_folders.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Top-Level Folders</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {repo.top_level_folders.map((folder) => (
                <Badge key={folder} variant="default">
                  {folder}/
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : null}

      {repo.project_structure ? (
        <Card>
          <CardHeader>
            <CardTitle>Project Structure</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="overflow-x-auto rounded-lg border border-border bg-surface-overlay p-4 font-mono text-xs leading-relaxed text-muted-foreground">
              {repo.project_structure}
            </pre>
          </CardContent>
        </Card>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Important Files
            </CardTitle>
          </CardHeader>
          <CardContent>
            {repo.important_files.length > 0 ? (
              <div className="space-y-2">
                {repo.important_files.map((file) => (
                  <div
                    key={file}
                    className="rounded-lg border border-border bg-surface-overlay px-3 py-2 font-mono text-xs text-foreground"
                  >
                    {file}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No important files ranked.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Play className="h-4 w-4" />
              Detected Entry Points
            </CardTitle>
          </CardHeader>
          <CardContent>
            {repo.entry_point_details.length > 0 ? (
              <div className="space-y-3">
                {repo.entry_point_details.map((entry) => (
                  <div
                    key={`${entry.path}-${entry.source}`}
                    className="rounded-lg border border-border bg-surface-overlay px-3 py-2.5"
                  >
                    <p className="font-mono text-xs text-foreground">{entry.path}</p>
                    <p className="mt-1 text-xs text-muted-foreground">{entry.reason}</p>
                    <Badge variant="outline" className="mt-2">
                      {entry.source}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No entry points detected.</p>
            )}
          </CardContent>
        </Card>
      </div>

      {repo.has_readme && repo.readme_preview ? (
        <Card>
          <CardHeader>
            <CardTitle>README Preview</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="max-h-64 overflow-y-auto whitespace-pre-wrap rounded-lg border border-border bg-surface-overlay p-4 text-xs leading-relaxed text-muted-foreground">
              {repo.readme_preview}
            </pre>
          </CardContent>
        </Card>
      ) : null}

      {repo.imports.frequent_packages.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Frequent External Packages</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {repo.imports.frequent_packages.map((pkg) => (
                <div
                  key={pkg.package}
                  className="flex items-center justify-between rounded-lg border border-border bg-surface-overlay px-3 py-2"
                >
                  <span className="font-mono text-xs text-foreground">{pkg.package}</span>
                  <Badge variant="outline">{pkg.count} files</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : null}
    </section>
  );
}
