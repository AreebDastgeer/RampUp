"use client";

import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  FileText,
  Package,
  TestTube,
  XCircle,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { SectionHeader } from "@/components/ui/section-header";
import { useAnalysis } from "@/lib/store/analysis-context";

type HealthSignal = {
  label: string;
  present: boolean;
  icon: React.ReactNode;
};

export function HealthPageContent() {
  const { analysis } = useAnalysis();
  const health = analysis!.repository.repository_health;
  const brief = analysis!.rampup_brief;

  const signals: HealthSignal[] = [
    {
      label: "README present",
      present: health.readme_present,
      icon: <FileText className="h-4 w-4" />,
    },
    {
      label: "License present",
      present: health.license_present,
      icon: <FileText className="h-4 w-4" />,
    },
    {
      label: "Tests detected",
      present: health.tests_detected,
      icon: <TestTube className="h-4 w-4" />,
    },
    {
      label: "Docker detected",
      present: health.docker_detected,
      icon: <Package className="h-4 w-4" />,
    },
    {
      label: "CI workflow detected",
      present: health.ci_workflow_detected,
      icon: <Activity className="h-4 w-4" />,
    },
    {
      label: "GitHub Actions detected",
      present: health.github_actions_detected,
      icon: <Activity className="h-4 w-4" />,
    },
    {
      label: "Env example detected",
      present: health.env_example_detected,
      icon: <FileText className="h-4 w-4" />,
    },
    {
      label: "Package manager detected",
      present: health.package_managers.length > 0,
      icon: <Package className="h-4 w-4" />,
    },
  ];

  const presentCount = signals.filter((s) => s.present).length;

  return (
    <section className="space-y-8">
      <SectionHeader
        title="Repository Health"
        description="Factual health signals computed automatically from the filesystem — not inferred by AI."
        badge={`${presentCount}/${signals.length} signals`}
        badgeVariant="success"
      />

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {signals.map((signal) => (
          <Card key={signal.label}>
            <CardContent className="flex items-center gap-3 pt-5">
              <div className="rounded-lg border border-border bg-surface-overlay p-2 text-muted-foreground">
                {signal.icon}
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-foreground">{signal.label}</p>
                <p className="text-xs text-muted-foreground">
                  {signal.present ? "Detected" : "Not detected"}
                </p>
              </div>
              {signal.present ? (
                <CheckCircle2 className="h-4 w-4 shrink-0 text-success" />
              ) : (
                <XCircle className="h-4 w-4 shrink-0 text-muted" />
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {health.package_managers.length > 0 ? (
        <Card>
          <CardContent className="py-5">
            <p className="text-sm font-medium text-foreground">Detected Package Managers</p>
            <p className="mt-2 text-sm text-muted-foreground">
              {health.package_managers.join(", ")}
            </p>
          </CardContent>
        </Card>
      ) : null}

      <div>
        <SectionHeader
          title="Detected Risks"
          description="Evidence-based onboarding risks — only surfaced when supported by repository analysis."
          badge="Potential Risks"
          badgeVariant="warning"
          className="mb-4"
        />
        <Card>
          <CardContent className="py-2">
            {brief?.potential_risks && brief.potential_risks.length > 0 ? (
              <div className="divide-y divide-border-subtle">
                {brief.potential_risks.map((risk, index) => (
                  <div key={index} className="flex gap-4 px-2 py-4">
                    <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-warning/30 bg-warning/10 text-warning">
                      <AlertTriangle className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="text-sm leading-relaxed text-foreground">{risk}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={<AlertTriangle className="h-5 w-5" />}
                title="No risks identified"
                description={
                  brief
                    ? "The AI brief did not surface any onboarding risks for this repository."
                    : "Risk analysis requires an AI-generated brief."
                }
                className="py-10"
              />
            )}
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
