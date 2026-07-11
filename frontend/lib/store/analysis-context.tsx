"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { analyzeRepository, AnalyzeApiError, checkBackendHealth } from "@/lib/api/analyze";
import type { AnalyzeResponse } from "@/lib/types/analysis";

type AnalysisContextValue = {
  analysis: AnalyzeResponse | null;
  hasAnalysis: boolean;
  loading: boolean;
  error: string;
  loadingMessage: string;
  analyze: (githubUrl: string, role: string, mission: string) => Promise<boolean>;
  clearAnalysis: () => void;
  clearError: () => void;
};

const LOADING_MESSAGES = [
  "Cloning repository...",
  "Running static code analysis...",
  "Generating AI onboarding brief...",
] as const;

const AnalysisContext = createContext<AnalysisContextValue | null>(null);

function isValidGithubUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    const host = parsed.hostname.replace(/^www\./, "");
    if (host !== "github.com") {
      return false;
    }
    const segments = parsed.pathname.split("/").filter(Boolean);
    return segments.length >= 2;
  } catch {
    return false;
  }
}

export function AnalysisProvider({ children }: { children: ReactNode }) {
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [loadingMessage, setLoadingMessage] = useState<string>(
    LOADING_MESSAGES[0]
  );
  const analyzingRef = useRef(false);

  const clearAnalysis = useCallback(() => {
    setAnalysis(null);
    setError("");
    setLoading(false);
    setLoadingMessage(LOADING_MESSAGES[0]);
    analyzingRef.current = false;
  }, []);

  const clearError = useCallback(() => {
    setError("");
  }, []);

  const analyze = useCallback(
    async (githubUrl: string, role: string, mission: string): Promise<boolean> => {
      if (analyzingRef.current) {
        return false;
      }

      const trimmedGithubUrl = githubUrl.trim();
      const trimmedMission = mission.trim();
      const trimmedRole = role.trim();

      if (!trimmedGithubUrl || !trimmedRole || !trimmedMission) {
        setError("Please provide a GitHub URL, role, and mission.");
        return false;
      }

      if (!isValidGithubUrl(trimmedGithubUrl)) {
        setError(
          "Please enter a valid public GitHub repository URL (e.g. https://github.com/owner/repo)."
        );
        return false;
      }

      analyzingRef.current = true;
      setError("");
      setLoading(true);
      setLoadingMessage(LOADING_MESSAGES[0]);

      let messageIndex = 0;
      const interval = setInterval(() => {
        messageIndex = (messageIndex + 1) % LOADING_MESSAGES.length;
        setLoadingMessage(LOADING_MESSAGES[messageIndex]);
      }, 2000);

      try {
        const backendAvailable = await checkBackendHealth();
        if (!backendAvailable) {
          setError(
            "Unable to reach the analysis server. Make sure the backend is running and try again."
          );
          return false;
        }

        const data = await analyzeRepository({
          github_url: trimmedGithubUrl,
          role: trimmedRole,
          mission: trimmedMission,
        });
        setAnalysis(data);
        return true;
      } catch (err) {
        const message =
          err instanceof AnalyzeApiError
            ? err.message
            : "Something went wrong while analyzing the repository. Make sure the backend is running and the GitHub URL is valid.";
        setError(message);
        return false;
      } finally {
        clearInterval(interval);
        setLoading(false);
        setLoadingMessage(LOADING_MESSAGES[0]);
        analyzingRef.current = false;
      }
    },
    []
  );

  const value = useMemo<AnalysisContextValue>(
    () => ({
      analysis,
      hasAnalysis: Boolean(analysis),
      loading,
      error,
      loadingMessage,
      analyze,
      clearAnalysis,
      clearError,
    }),
    [analysis, loading, error, loadingMessage, analyze, clearAnalysis, clearError]
  );

  return (
    <AnalysisContext.Provider value={value}>{children}</AnalysisContext.Provider>
  );
}

export function useAnalysis() {
  const context = useContext(AnalysisContext);
  if (!context) {
    throw new Error("useAnalysis must be used within an AnalysisProvider");
  }
  return context;
}
