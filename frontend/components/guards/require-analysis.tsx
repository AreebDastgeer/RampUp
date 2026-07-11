"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAnalysis } from "@/lib/store/analysis-context";

type RequireAnalysisProps = {
  children: React.ReactNode;
};

export function RequireAnalysis({ children }: RequireAnalysisProps) {
  const { hasAnalysis, loading } = useAnalysis();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !hasAnalysis) {
      router.replace("/");
    }
  }, [hasAnalysis, loading, router]);

  if (!hasAnalysis) {
    return null;
  }

  return <>{children}</>;
}
