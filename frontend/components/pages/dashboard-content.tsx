"use client";

import Link from "next/link";
import {
  ArrowRight,
  Boxes,
  FileCode2,
  FolderTree,
  GitBranch,
  Target,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SectionHeader } from "@/components/ui/section-header";
import { useAnalysis } from "@/lib/store/analysis-context";
import type { AppRoute } from "@/lib/navigation";

const QUICK_LINKS: { href: AppRoute; label: string; description: string }[] = [
  {
    href: "/repository",
    label: "Repository",
    description: "Structure, technologies, and entry points",
  },
  {
    href: "/mission",
    label: "Mission",
    description: "Reading order and implementation roadmap",
  },
  {
    href: "/architecture",
    label: "Architecture",
    description: "API routes, dependencies, and execution flow",
  },
  {
    href: "/health",
    label: "Health & Risks",
    description: "Health signals and onboarding risks",
  },
];

export function DashboardPageContent() {
  const { analysis } = useAnalysis();
  const repo = analysis!.repository;
  const brief = analysis!.rampup_brief;

  return (
    <section className="space-y-6">
      <SectionHeader
        title="Dashboard"
        description="High-level summary of your analyzed repository and quick navigation to detailed views."
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

      {brief ? (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-4 w-4 text-accent" />
              Mission Summary
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm leading-relaxed text-muted-foreground">
              {brief.repository_snapshot}
            </p>
            <div className="flex flex-wrap gap-3">
              <Badge variant="accent">{analysis!.role}</Badge>
              <Badge variant="outline">{brief.estimated_difficulty}</Badge>
              <Badge variant="outline">{brief.estimated_time_to_first_contribution}</Badge>
            </div>
            <p className="text-sm text-foreground">
              <span className="font-medium">Mission: </span>
              {analysis!.mission}
            </p>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="py-5">
            <p className="text-sm text-muted-foreground">
              The repository analysis completed successfully, but the AI response exceeded the
              model&apos;s output limit.
            </p>
            <p className="mt-2 text-sm text-muted-foreground">
              Please retry or reduce repository context.
            </p>
          </CardContent>
        </Card>
      )}

      <div>
        <h3 className="mb-4 text-sm font-semibold text-foreground">Quick Navigation</h3>
        <div className="grid gap-3 sm:grid-cols-2">
          {QUICK_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="group flex items-center justify-between rounded-xl border border-border bg-surface-overlay px-4 py-3 transition-colors hover:border-accent/30 hover:bg-accent-muted/30"
            >
              <div>
                <p className="text-sm font-medium text-foreground">{link.label}</p>
                <p className="mt-0.5 text-xs text-muted-foreground">{link.description}</p>
              </div>
              <ArrowRight className="h-4 w-4 text-muted-foreground transition-transform group-hover:translate-x-0.5 group-hover:text-accent" />
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}
