"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/app-shell";
import { AnalyzeForm } from "@/components/analyze-form";
import { FeatureCards } from "@/components/home/feature-cards";
import { HowItWorks } from "@/components/home/how-it-works";
import { useAnalysis } from "@/lib/store/analysis-context";

export default function HomePage() {
  const router = useRouter();
  const { loading, error, loadingMessage, analyze } = useAnalysis();

  const [githubUrl, setGithubUrl] = useState("");
  const [role, setRole] = useState("");
  const [mission, setMission] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (loading) {
      return;
    }

    const success = await analyze(githubUrl, role, mission);
    if (success) {
      router.push("/dashboard");
    }
  }

  return (
    <AppShell>
      <div className="space-y-16 pb-8">
        <div className="flex flex-col items-center pt-4">
          <div className="mb-10 max-w-2xl text-center">
            <p className="mb-4 inline-flex items-center rounded-full border border-accent/20 bg-accent-muted px-3 py-1 text-xs font-medium text-accent-foreground">
              Repository Intelligence Engine
            </p>
            <h2 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
              Onboard to any codebase with confidence
            </h2>
            <p className="mt-4 text-sm leading-relaxed text-muted-foreground sm:text-base">
              RampUp performs real static analysis before the AI explains what matters —
              entry points, routes, dependencies, and health signals.
            </p>
          </div>

          <AnalyzeForm
            githubUrl={githubUrl}
            role={role}
            mission={mission}
            loading={loading}
            loadingMessage={loadingMessage}
            error={error}
            onGithubUrlChange={setGithubUrl}
            onRoleChange={setRole}
            onMissionChange={setMission}
            onSubmit={handleSubmit}
          />
        </div>

        {!loading ? (
          <>
            <div className="flex flex-col items-center">
              <FeatureCards />
            </div>

            <div className="flex flex-col items-center">
              <HowItWorks />
            </div>
          </>
        ) : null}
      </div>
    </AppShell>
  );
}
