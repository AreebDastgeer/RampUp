"use client";

import { FormEvent } from "react";
import { Loader2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const roles = [
  "Frontend Developer",
  "Backend Developer",
  "Full Stack Developer",
  "DevOps Engineer",
  "ML Engineer",
  "QA Engineer",
  "New Intern",
] as const;

type AnalyzeFormProps = {
  githubUrl: string;
  role: string;
  mission: string;
  loading: boolean;
  loadingMessage: string;
  error: string;
  onGithubUrlChange: (value: string) => void;
  onRoleChange: (value: string) => void;
  onMissionChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
};

export function AnalyzeForm({
  githubUrl,
  role,
  mission,
  loading,
  loadingMessage,
  error,
  onGithubUrlChange,
  onRoleChange,
  onMissionChange,
  onSubmit,
}: AnalyzeFormProps) {
  return (
    <Card className="mx-auto w-full max-w-xl border-border/80 bg-surface-raised/90 backdrop-blur-sm">
      <CardHeader className="text-center">
        <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-accent-muted text-accent">
          <Sparkles className="h-5 w-5" />
        </div>
        <CardTitle className="text-xl">Start your ramp-up</CardTitle>
        <CardDescription>
          Share the repository and your mission. RampUp will analyze the codebase
          before generating your onboarding brief.
        </CardDescription>
      </CardHeader>

      <CardContent>
        <form className="space-y-5" onSubmit={onSubmit}>
          <div className="space-y-2">
            <label htmlFor="github-url" className="text-sm font-medium text-foreground">
              GitHub Repository URL
            </label>
            <input
              id="github-url"
              name="github-url"
              type="url"
              value={githubUrl}
              onChange={(e) => onGithubUrlChange(e.target.value)}
              placeholder="https://github.com/organization/repository"
              disabled={loading}
              className="h-11 w-full rounded-lg border border-border bg-surface px-4 text-sm text-foreground outline-none transition-colors placeholder:text-muted focus:border-accent/50 focus:ring-2 focus:ring-[var(--ring)] disabled:cursor-not-allowed disabled:opacity-60"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="role" className="text-sm font-medium text-foreground">
              Role
            </label>
            <select
              id="role"
              name="role"
              value={role}
              onChange={(e) => onRoleChange(e.target.value)}
              disabled={loading}
              className="h-11 w-full appearance-none rounded-lg border border-border bg-surface px-4 text-sm text-foreground outline-none transition-colors focus:border-accent/50 focus:ring-2 focus:ring-[var(--ring)] disabled:cursor-not-allowed disabled:opacity-60"
            >
              <option value="" disabled>
                Select your role
              </option>
              {roles.map((roleOption) => (
                <option key={roleOption} value={roleOption}>
                  {roleOption}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <label htmlFor="mission" className="text-sm font-medium text-foreground">
              Mission
            </label>
            <textarea
              id="mission"
              name="mission"
              rows={4}
              value={mission}
              onChange={(e) => onMissionChange(e.target.value)}
              placeholder="What do you need to understand or accomplish in this codebase?"
              disabled={loading}
              className="w-full resize-y rounded-lg border border-border bg-surface px-4 py-3 text-sm text-foreground outline-none transition-colors placeholder:text-muted focus:border-accent/50 focus:ring-2 focus:ring-[var(--ring)] disabled:cursor-not-allowed disabled:opacity-60"
            />
          </div>

          {loading ? (
            <div className="rounded-lg border border-accent/20 bg-accent-muted/50 px-4 py-3">
              <div className="flex items-center gap-3">
                <Loader2 className="h-4 w-4 shrink-0 animate-spin text-accent" />
                <div>
                  <p className="text-sm font-medium text-foreground">Analyzing repository</p>
                  <p className="mt-0.5 text-xs text-muted-foreground">{loadingMessage}</p>
                </div>
              </div>
            </div>
          ) : null}

          {error ? (
            <div className="rounded-lg border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger">
              {error}
            </div>
          ) : null}

          <Button type="submit" disabled={loading} className="w-full" size="lg">
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                {loadingMessage}
              </>
            ) : (
              "Start Ramp-Up"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
