"use client";

import { AppShell } from "@/components/layout/app-shell";
import { RequireAnalysis } from "@/components/guards/require-analysis";
import { RepositoryPageContent } from "@/components/pages/repository-content";

export default function RepositoryPage() {
  return (
    <AppShell>
      <RequireAnalysis>
        <RepositoryPageContent />
      </RequireAnalysis>
    </AppShell>
  );
}
