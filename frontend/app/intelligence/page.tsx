"use client";

import { AppShell } from "@/components/layout/app-shell";
import { RequireAnalysis } from "@/components/guards/require-analysis";
import { IntelligencePageContent } from "@/components/pages/intelligence-content";

export default function IntelligencePage() {
  return (
    <AppShell>
      <RequireAnalysis>
        <IntelligencePageContent />
      </RequireAnalysis>
    </AppShell>
  );
}
