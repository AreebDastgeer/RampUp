export type AppRoute =
  | "/"
  | "/dashboard"
  | "/mission"
  | "/architecture"
  | "/intelligence"
  | "/repository"
  | "/health";

  export type DashboardSection =
  | "overview"
  | "mission-map"
  | "reading-order"
  | "execution-flow"
  | "dependency-explorer"
  | "api-explorer"
  | "repository-health"
  | "code-intelligence"
  | "roadmap"
  | "risks";
  
export type NavItem = {
  href: AppRoute;
  label: string;
  description: string;
  group: "home" | "intelligence" | "onboarding" | "analysis";
  requiresAnalysis: boolean;
};

export const NAV_ITEMS: NavItem[] = [
  {
    href: "/",
    label: "Home",
    description: "Analyze a repository and get started",
    group: "home",
    requiresAnalysis: false,
  },
  {
    href: "/dashboard",
    label: "Dashboard",
    description: "High-level repository summary and quick navigation",
    group: "intelligence",
    requiresAnalysis: true,
  },
  {
    href: "/repository",
    label: "Repository",
    description: "Overview, technologies, structure, and entry points",
    group: "intelligence",
    requiresAnalysis: true,
  },
  {
    href: "/intelligence",
    label: "Code Intelligence",
    description: "Classes, functions, packages, and dependency insights",
    group: "intelligence",
    requiresAnalysis: true,
  },
  {
    href: "/architecture",
    label: "Architecture",
    description: "Execution flow, dependencies, and API explorer",
    group: "onboarding",
    requiresAnalysis: true,
  },
  {
    href: "/mission",
    label: "Mission",
    description: "Mission map, reading order, and implementation roadmap",
    group: "onboarding",
    requiresAnalysis: true,
  },
  {
    href: "/health",
    label: "Health & Risks",
    description: "Repository health signals and detected risks",
    group: "analysis",
    requiresAnalysis: true,
  },
];

export const NAV_GROUPS = [
  { id: "home", label: "Get Started" },
  { id: "intelligence", label: "Repository Intelligence" },
  { id: "onboarding", label: "Onboarding Brief" },
  { id: "analysis", label: "Risk Analysis" },
] as const;

export function getNavItem(pathname: string): NavItem | undefined {
  return NAV_ITEMS.find((item) => item.href === pathname);
}
