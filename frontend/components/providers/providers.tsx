import { AnalysisProvider } from "@/lib/store/analysis-context";

export function Providers({ children }: { children: React.ReactNode }) {
  return <AnalysisProvider>{children}</AnalysisProvider>;
}
