"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  Activity,
  Brain,
  GitBranch,
  Home,
  LayoutDashboard,
  Lock,
  Map,
  Network,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import {
  NAV_GROUPS,
  NAV_ITEMS,
  type AppRoute,
  type NavItem,
} from "@/lib/navigation";

const ICONS: Record<AppRoute, React.ReactNode> = {
  "/": <Home className="h-4 w-4" />,
  "/dashboard": <LayoutDashboard className="h-4 w-4" />,
  "/repository": <GitBranch className="h-4 w-4" />,
  "/intelligence": <Brain className="h-4 w-4" />,
  "/architecture": <Network className="h-4 w-4" />,
  "/mission": <Map className="h-4 w-4" />,
  "/health": <Activity className="h-4 w-4" />,
};

type SidebarProps = {
  collapsed?: boolean;
  hasAnalysis?: boolean;
  onNavigate?: () => void;
};

function NavButton({
  item,
  active,
  locked,
  onNavigate,
}: {
  item: NavItem;
  active: boolean;
  locked: boolean;
  onNavigate?: () => void;
}) {
  const content = (
    <>
      {active && !locked ? (
        <motion.span
          layoutId="sidebar-active"
          className="absolute inset-0 rounded-lg border border-accent/20 bg-accent-muted"
          transition={{ type: "spring", stiffness: 380, damping: 32 }}
        />
      ) : null}
      <span
        className={cn(
          "relative z-10 text-muted-foreground",
          !locked && "group-hover:text-foreground",
          active && !locked && "text-foreground"
        )}
      >
        {ICONS[item.href]}
      </span>
      <span className="relative z-10 flex min-w-0 flex-1 flex-col">
        <span className="truncate font-medium">{item.label}</span>
      </span>
      {locked ? (
        <Lock className="relative z-10 h-3.5 w-3.5 shrink-0 text-muted" />
      ) : null}
    </>
  );

  const className = cn(
    "group relative flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition-colors",
    locked
      ? "cursor-not-allowed text-muted opacity-50"
      : active
        ? "bg-accent-muted text-foreground"
        : "text-muted-foreground hover:bg-surface-overlay hover:text-foreground"
  );

  if (locked) {
    return (
      <div className={className} aria-disabled="true" title="Analyze a repository to unlock">
        {content}
      </div>
    );
  }

  return (
    <Link href={item.href} className={className} onClick={onNavigate}>
      {content}
    </Link>
  );
}

export function Sidebar({
  collapsed = false,
  hasAnalysis = false,
  onNavigate,
}: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "flex h-full flex-col border-r border-border bg-surface",
        collapsed ? "w-16" : "w-[var(--sidebar-width)]"
      )}
    >
      <div className="flex h-[var(--topbar-height)] items-center gap-3 border-b border-border px-4">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent text-sm font-bold text-white">
          R
        </div>
        {!collapsed ? (
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold tracking-tight">RampUp</p>
            <p className="truncate text-xs text-muted-foreground">Repository Intelligence</p>
          </div>
        ) : null}
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-4">
        {NAV_GROUPS.map((group) => {
          const items = NAV_ITEMS.filter((item) => item.group === group.id);
          return (
            <div key={group.id} className="mb-6 last:mb-0">
              {!collapsed ? (
                <p className="mb-2 px-3 text-[11px] font-semibold uppercase tracking-wider text-muted">
                  {group.label}
                </p>
              ) : null}
              <div className="space-y-1">
                {items.map((item) => {
                  const locked = item.requiresAnalysis && !hasAnalysis;
                  return (
                    <NavButton
                      key={item.href}
                      item={item}
                      active={pathname === item.href}
                      locked={locked}
                      onNavigate={onNavigate}
                    />
                  );
                })}
              </div>
            </div>
          );
        })}
      </nav>

      <div className="border-t border-border p-4">
        {!collapsed ? (
          <div className="rounded-lg border border-border bg-surface-overlay p-3">
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs font-medium text-muted-foreground">Analysis</span>
              <Badge variant={hasAnalysis ? "success" : "outline"}>
                {hasAnalysis ? "Ready" : "Pending"}
              </Badge>
            </div>
            <p className="mt-2 text-xs leading-relaxed text-muted">
              {hasAnalysis
                ? "Repository intelligence loaded."
                : "Submit a repo to unlock sections."}
            </p>
          </div>
        ) : null}
      </div>
    </aside>
  );
}
