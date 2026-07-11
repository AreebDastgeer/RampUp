"use client";

import { AppShell } from "@/components/layout/app-shell";
import { RequireAnalysis } from "@/components/guards/require-analysis";
import { HealthPageContent } from "@/components/pages/health-content";

export default function HealthPage() {
  return (
    <AppShell>
      <RequireAnalysis>
        <HealthPageContent />
      </RequireAnalysis>
    </AppShell>
  );
}
