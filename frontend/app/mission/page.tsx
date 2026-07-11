"use client";

import { AppShell } from "@/components/layout/app-shell";
import { RequireAnalysis } from "@/components/guards/require-analysis";
import { MissionPageContent } from "@/components/pages/mission-content";

export default function MissionPage() {
  return (
    <AppShell>
      <RequireAnalysis>
        <MissionPageContent />
      </RequireAnalysis>
    </AppShell>
  );
}
