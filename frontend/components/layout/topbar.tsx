"use client";

import { usePathname, useRouter } from "next/navigation";
import { Menu, Plus, Search, Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { getNavItem } from "@/lib/navigation";
import { useAnalysis } from "@/lib/store/analysis-context";

const AI_BRIEF_TARGET_ID = "ai-onboarding-brief";

type TopBarProps = {
  onMenuClick?: () => void;
  onSearchClick?: () => void;
  className?: string;
};

export function TopBar({ onMenuClick, onSearchClick, className }: TopBarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { analysis, hasAnalysis, clearAnalysis } = useAnalysis();
  const hasAiBrief = Boolean(analysis?.rampup_brief);

  const navItem = getNavItem(pathname);
  const repositoryName = analysis?.repository.name;
  const role = analysis?.role;

  function handleNewAnalysis() {
    clearAnalysis();
    router.push("/");
  }

  function scrollToAiBrief() {
    const target = document.getElementById(AI_BRIEF_TARGET_ID);
    if (!target) {
      return false;
    }

    target.scrollIntoView({ behavior: "smooth", block: "start" });
    return true;
  }

  function handleAiBriefClick() {
    if (!hasAiBrief) {
      return;
    }

    if (pathname === "/mission" && scrollToAiBrief()) {
      return;
    }

    router.push("/mission");

    let attempts = 0;
    const waitForTarget = () => {
      if (scrollToAiBrief() || attempts >= 30) {
        return;
      }

      attempts += 1;
      window.setTimeout(waitForTarget, 50);
    };

    window.setTimeout(waitForTarget, 50);
  }

  return (
    <header
      className={cn(
        "flex h-[var(--topbar-height)] items-center justify-between gap-4 border-b border-border bg-surface/80 px-4 backdrop-blur-md sm:px-6",
        className
      )}
    >
      <div className="flex min-w-0 items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={onMenuClick}
          aria-label="Open navigation"
        >
          <Menu className="h-4 w-4" />
        </Button>

        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="truncate text-sm font-semibold text-foreground sm:text-base">
              {navItem?.label ?? "RampUp"}
            </h1>
            {repositoryName && hasAnalysis ? (
              <Badge variant="accent" className="hidden sm:inline-flex">
                {repositoryName}
              </Badge>
            ) : null}
          </div>
          <p className="hidden truncate text-xs text-muted-foreground sm:block">
            {navItem?.description}
            {role ? ` · ${role}` : ""}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={onSearchClick}
          className="hidden items-center gap-2 rounded-lg border border-border bg-surface-overlay px-3 py-2 text-muted-foreground transition-colors hover:bg-surface-raised hover:text-foreground md:flex"
          aria-label="Search sections"
        >
          <Search className="h-3.5 w-3.5" />
          <span className="text-xs">Search sections</span>
          <kbd className="rounded border border-border bg-surface px-1.5 py-0.5 font-mono text-[10px]">
            ⌘K
          </kbd>
        </button>

        {hasAnalysis ? (
          <Button
            variant="secondary"
            size="sm"
            className="hidden sm:inline-flex"
            onClick={handleAiBriefClick}
            disabled={!hasAiBrief}
            title={hasAiBrief ? "Open the AI onboarding brief" : "AI brief unavailable"}
          >
            <Sparkles className="h-3.5 w-3.5" />
            AI Brief
          </Button>
        ) : null}

        {hasAnalysis ? (
          <Button variant="outline" size="sm" onClick={handleNewAnalysis}>
            <Plus className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">New Analysis</span>
          </Button>
        ) : null}
      </div>
    </header>
  );
}
