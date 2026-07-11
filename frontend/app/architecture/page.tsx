"use client";

import { AppShell } from "@/components/layout/app-shell";
import { RequireAnalysis } from "@/components/guards/require-analysis";
import { ArchitecturePageContent } from "@/components/pages/architecture-content";

export default function ArchitecturePage() {
  return (
    <AppShell>
      <RequireAnalysis>
        <ArchitecturePageContent />
      </RequireAnalysis>
    </AppShell>
  );
}
