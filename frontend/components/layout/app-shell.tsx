"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { Sidebar } from "@/components/layout/sidebar";
import { TopBar } from "@/components/layout/topbar";
import { SectionSearchPalette } from "@/components/layout/section-search-palette";
import { PageTransition } from "@/components/layout/page-transition";
import { useAnalysis } from "@/lib/store/analysis-context";

type AppShellProps = {
  children: React.ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [sectionSearchOpen, setSectionSearchOpen] = useState(false);
  const pathname = usePathname();
  const { hasAnalysis } = useAnalysis();

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setSectionSearchOpen(true);
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="flex min-h-screen bg-background text-foreground">
      <div className="hidden lg:block">
        <Sidebar hasAnalysis={hasAnalysis} />
      </div>

      {mobileNavOpen ? (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            aria-label="Close navigation"
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setMobileNavOpen(false)}
          />
          <div className="relative z-10 h-full w-[var(--sidebar-width)] shadow-2xl">
            <Sidebar
              hasAnalysis={hasAnalysis}
              onNavigate={() => setMobileNavOpen(false)}
            />
          </div>
        </div>
      ) : null}

      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar
          onMenuClick={() => setMobileNavOpen(true)}
          onSearchClick={() => setSectionSearchOpen(true)}
        />

        <main className="relative flex-1 overflow-y-auto bg-grid">
          <div className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
            <PageTransition sectionKey={pathname}>{children}</PageTransition>
          </div>
        </main>
      </div>

      {sectionSearchOpen ? (
        <SectionSearchPalette
          open={sectionSearchOpen}
          onOpenChange={setSectionSearchOpen}
          hasAnalysis={hasAnalysis}
        />
      ) : null}
    </div>
  );
}
