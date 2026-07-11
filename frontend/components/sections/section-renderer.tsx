import type { DashboardSection } from "@/lib/navigation";
import { ApiExplorerSection } from "@/components/sections/api-explorer";
import { CodeIntelligenceSection } from "@/components/sections/code-intelligence";
import { DependencyExplorerSection } from "@/components/sections/dependency-explorer";
import { ExecutionFlowSection } from "@/components/sections/execution-flow";
import { MissionMapSection } from "@/components/sections/mission-map";
import { ReadingOrderSection } from "@/components/sections/reading-order";
import { RepositoryHealthSection } from "@/components/sections/repository-health";
import { RepositoryOverviewSection } from "@/components/sections/repository-overview";
import { RoadmapSection } from "@/components/sections/roadmap";
import { RisksSection } from "@/components/sections/risks";

type SectionRendererProps = {
  section: DashboardSection;
  hasData?: boolean;
  loading?: boolean;
};

export function SectionRenderer({ section, hasData, loading }: SectionRendererProps) {
  switch (section) {
    case "overview":
      return <RepositoryOverviewSection hasData={hasData} loading={loading} />;
    case "mission-map":
      return <MissionMapSection hasData={hasData} />;
    case "reading-order":
      return <ReadingOrderSection hasData={hasData} />;
    case "execution-flow":
      return <ExecutionFlowSection hasData={hasData} />;
    case "dependency-explorer":
      return <DependencyExplorerSection hasData={hasData} />;
    case "api-explorer":
      return <ApiExplorerSection hasData={hasData} />;
    case "repository-health":
      return <RepositoryHealthSection hasData={hasData} />;
    case "code-intelligence":
      return <CodeIntelligenceSection hasData={hasData} />;
    case "roadmap":
      return <RoadmapSection hasData={hasData} />;
    case "risks":
      return <RisksSection hasData={hasData} />;
    default:
      return null;
  }
}
