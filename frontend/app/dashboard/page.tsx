"use client";

import { AppShell } from "@/components/layout/app-shell";
import { RequireAnalysis } from "@/components/guards/require-analysis";
import { DashboardPageContent } from "@/components/pages/dashboard-content";

export default function DashboardPage() {
  return (
    <AppShell>
      <RequireAnalysis>
        <DashboardPageContent />
      </RequireAnalysis>
    </AppShell>
  );
}
