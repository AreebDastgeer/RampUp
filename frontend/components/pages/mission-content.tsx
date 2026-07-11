"use client";

import { BookOpen, GitBranch, Map } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { SectionHeader } from "@/components/ui/section-header";
import { useAnalysis } from "@/lib/store/analysis-context";
import type { Confidence } from "@/lib/types/analysis";

function confidenceVariant(confidence: Confidence): "success" | "warning" | "outline" {
  if (confidence === "high") return "success";
  if (confidence === "medium") return "warning";
  return "outline";
}

export function MissionPageContent() {
  const { analysis } = useAnalysis();
  const brief = analysis!.rampup_brief;

  if (!brief) {
    return (
      <section className="space-y-6">
        <SectionHeader
          title="Mission"
          description="Mission-aligned focus areas derived from your role, task, and detected repository structure."
          badge="AI brief unavailable"
          badgeVariant="outline"
        />
        <EmptyState
          icon={<Map className="h-5 w-5" />}
          title="AI brief not generated"
          description="The onboarding brief requires a configured AI backend. Repository intelligence is still available on other pages."
          className="py-12"
        />
      </section>
    );
  }

  return (
    <section id="ai-onboarding-brief" className="space-y-8 scroll-mt-24">
      <SectionHeader
        title="AI Onboarding Brief"
        description="Mission-aligned focus areas derived from your role, task, and detected repository structure."
        badge="AI-powered"
        badgeVariant="accent"
      />

      <div>
        <SectionHeader
          title="Mission Map"
          description="Concepts and focus areas aligned to your mission."
          className="mb-4"
        />
        <div className="grid gap-4 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Concepts to Understand</CardTitle>
            </CardHeader>
            <CardContent>
              {brief.understand_first.length > 0 ? (
                <div className="space-y-3">
                  {brief.understand_first.map((item) => (
                    <div
                      key={item.concept}
                      className="rounded-lg border border-border bg-surface-overlay px-3 py-2.5"
                    >
                      <p className="text-sm font-medium text-foreground">{item.concept}</p>
                      <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
                        {item.reason}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No concepts listed.</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Start Here</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed text-muted-foreground">
                {brief.repository_navigation?.start_here ?? "No starting point specified."}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Mission Alignment</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-foreground">
                <span className="font-medium">Role: </span>
                {analysis!.role}
              </p>
              <p className="text-sm text-foreground">
                <span className="font-medium">Mission: </span>
                {analysis!.mission}
              </p>
              <div className="mt-3 flex flex-col gap-4">
  <div className="rounded-3xl border border-accent/20 bg-accent/10 p-5">
    <p className="text-sm leading-7 text-foreground">
      {brief.estimated_difficulty}
    </p>
  </div>

  <div className="rounded-3xl border border-border bg-surface-overlay p-5">
    <p className="text-sm leading-7 text-muted-foreground">
      {brief.estimated_time_to_first_contribution}
    </p>
  </div>
</div>
            </CardContent>
          </Card>
        </div>
      </div>

      <div>
        <SectionHeader
          title="Reading Order"
          description="Prioritized files to inspect first — ranked by usefulness and mission relevance."
          badge="Open These Files"
          badgeVariant="outline"
          className="mb-4"
        />
        <Card>
          <CardContent className="py-2">
            {brief.open_these_files.length > 0 ? (
              <div className="divide-y divide-border-subtle">
                {brief.open_these_files.map((file, index) => (
                  <div key={file.path} className="flex items-center gap-4 px-2 py-4">
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-border bg-surface-overlay text-xs font-semibold text-muted-foreground">
                      {index + 1}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="font-mono text-sm text-foreground">{file.path}</p>
                      <p className="mt-1 text-sm text-muted-foreground">{file.reason}</p>
                    </div>
                    <Badge variant={confidenceVariant(file.confidence)}>
                      {file.confidence}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={<BookOpen className="h-5 w-5" />}
                title="No reading order generated"
                description="The AI brief did not include file recommendations."
                className="py-10"
              />
            )}
          </CardContent>
        </Card>
      </div>

      <div>
        <SectionHeader
          title="Implementation Roadmap"
          description="Suggested implementation sequence from the AI brief."
          badge="Implementation Plan"
          badgeVariant="outline"
          className="mb-4"
        />
        <Card>
          <CardContent className="py-6">
            {brief.implementation_plan.length > 0 ? (
              <ol className="relative space-y-4 border-l border-border pl-8">
                {brief.implementation_plan.map((step, index) => (
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
                icon={<GitBranch className="h-5 w-5" />}
                title="No roadmap generated"
                description="The AI brief did not include an implementation plan."
              />
            )}
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
