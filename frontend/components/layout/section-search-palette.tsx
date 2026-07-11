"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Search } from "lucide-react";
import { NAV_GROUPS, NAV_ITEMS, type NavItem } from "@/lib/navigation";
import { cn } from "@/lib/utils";

type SectionSearchPaletteProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  hasAnalysis: boolean;
};

function getSearchableText(item: NavItem) {
  return [item.label, item.description, item.group].join(" ").toLowerCase();
}

export function SectionSearchPalette({
  open,
  onOpenChange,
  hasAnalysis,
}: SectionSearchPaletteProps) {
  const router = useRouter();
  const pathname = usePathname();
  const inputRef = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      inputRef.current?.focus();
      inputRef.current?.select();
    }, 0);

    return () => window.clearTimeout(timeout);
  }, [open]);

  const results = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();

    return NAV_ITEMS.filter((item) => {
      if (!normalizedQuery) {
        return true;
      }

      return getSearchableText(item).includes(normalizedQuery);
    });
  }, [query]);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onOpenChange(false);
      }
    }

    if (!open) {
      return;
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, onOpenChange]);

  function handleSelect(item: NavItem) {
    if (item.requiresAnalysis && !hasAnalysis) {
      return;
    }

    onOpenChange(false);
    router.push(item.href);
  }

  if (!open) {
    return null;
  }

  const groupedResults = NAV_GROUPS.map((group) => ({
    ...group,
    items: results.filter((item) => item.group === group.id),
  })).filter((group) => group.items.length > 0);

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/55 px-4 py-20 backdrop-blur-sm">
      <button
        type="button"
        aria-label="Close section search"
        className="absolute inset-0 cursor-default"
        onClick={() => onOpenChange(false)}
      />

      <div className="relative z-10 w-full max-w-2xl overflow-hidden rounded-2xl border border-border bg-surface-raised shadow-2xl shadow-black/30">
        <div className="flex items-center gap-3 border-b border-border px-4 py-4">
          <Search className="h-4 w-4 shrink-0 text-muted-foreground" />
          <input
            ref={inputRef}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search sections, pages, and descriptions"
            className="h-10 w-full bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground"
            aria-label="Search sections"
          />
          <kbd className="rounded border border-border bg-surface px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground">
            Esc
          </kbd>
        </div>

        <div className="max-h-[60vh] overflow-y-auto p-2">
          {groupedResults.length > 0 ? (
            groupedResults.map((group) => (
              <div key={group.id} className="mb-2 last:mb-0">
                <p className="px-3 py-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                  {group.label}
                </p>
                <div className="space-y-2">
                  {group.items.map((item) => {
                    const locked = item.requiresAnalysis && !hasAnalysis;
                    const active = pathname === item.href;

                    return (
                      <button
                        key={item.href}
                        type="button"
                        onClick={() => handleSelect(item)}
                        className={cn(
                          "flex w-full items-start gap-3 rounded-xl px-3 py-3.5 text-left transition-colors",
                          locked
                            ? "cursor-not-allowed opacity-50"
                            : "hover:bg-surface-overlay",
                          active && !locked && "bg-accent-muted/50"
                        )}
                        disabled={locked}
                      >
                        <span className="mt-0.5 h-2.5 w-2.5 rounded-full bg-accent/70" />
                        <span className="min-w-0 flex-1">
                          <span className="block text-sm font-medium leading-snug text-foreground">
                            {item.label}
                          </span>
                          <span className="mt-1.5 block text-xs leading-relaxed text-muted-foreground">
                            {item.description}
                          </span>
                        </span>
                        <span className="shrink-0 text-[11px] font-medium text-muted-foreground">
                          {locked ? "Locked" : active ? "Current" : "Open"}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))
          ) : (
            <div className="px-4 py-10 text-center text-sm text-muted-foreground">
              No sections match your search.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}