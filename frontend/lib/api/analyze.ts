import type { AnalyzeRequest, AnalyzeResponse } from "@/lib/types/analysis";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

/** Analysis can take several minutes (clone + static analysis + LLM). */
const ANALYZE_TIMEOUT_MS = 5 * 60 * 1000;

export class AnalyzeApiError extends Error {
  constructor(
    message: string,
    public readonly status?: number
  ) {
    super(message);
    this.name = "AnalyzeApiError";
  }
}

async function parseErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string" && body.detail.trim()) {
      return body.detail;
    }
    if (Array.isArray(body.detail) && body.detail.length > 0) {
      const first = body.detail[0] as { msg?: string };
      if (typeof first?.msg === "string") {
        return first.msg;
      }
    }
  } catch {
    // Response body is not JSON — fall through to defaults.
  }

  if (response.status === 400 || response.status === 422) {
    return "We couldn't analyze that repository. Please check the URL and try again.";
  }

  if (response.status >= 500) {
    return "The analysis server encountered an error. Make sure the backend is running and try again.";
  }

  return "Analysis failed. Please check your inputs and try again.";
}

export async function analyzeRepository(
  request: AnalyzeRequest
): Promise<AnalyzeResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), ANALYZE_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
      signal: controller.signal,
    });

    if (!response.ok) {
      const message = await parseErrorMessage(response);
      throw new AnalyzeApiError(message, response.status);
    }

    return response.json() as Promise<AnalyzeResponse>;
  } catch (err) {
    if (err instanceof AnalyzeApiError) {
      throw err;
    }

    if (err instanceof DOMException && err.name === "AbortError") {
      throw new AnalyzeApiError(
        "Analysis timed out. The repository may be too large — try again or use a smaller repo."
      );
    }

    if (err instanceof TypeError) {
      throw new AnalyzeApiError(
        `Unable to reach the analysis server at ${API_BASE_URL}. Make sure the backend is running.`
      );
    }

    throw new AnalyzeApiError(
      "Something went wrong while analyzing the repository. Please try again."
    );
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/`, {
      signal: AbortSignal.timeout(5000),
    });
    return response.ok;
  } catch {
    return false;
  }
}
