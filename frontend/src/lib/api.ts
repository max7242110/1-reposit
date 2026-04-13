import {
  ACModelDetail,
  ACModelSummary,
  Methodology,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
const FETCH_TIMEOUT_MS = 10_000;

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

async function apiFetch<T>(path: string): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);

  try {
    const res = await fetch(`${API_BASE}${path}`, {
      signal: controller.signal,
      next: { revalidate: 60 },
    });

    if (!res.ok) {
      throw new ApiError(res.status, `API ${path}: ${res.status} ${res.statusText}`);
    }

    const contentType = res.headers.get("content-type") || "";
    if (!contentType.includes("application/json")) {
      throw new ApiError(res.status, `API ${path}: unexpected content-type ${contentType}`);
    }

    try {
      return (await res.json()) as T;
    } catch {
      throw new ApiError(res.status, `API ${path}: invalid JSON in response body`);
    }
  } finally {
    clearTimeout(timeout);
  }
}

// v2 API
export async function getModels(params?: Record<string, string>): Promise<ACModelSummary[]> {
  const query = params ? "?" + new URLSearchParams(params).toString() : "";
  const data = await apiFetch<ACModelSummary[] | PaginatedResponse<ACModelSummary>>(
    `/v2/models/${query}`,
  );
  return Array.isArray(data) ? data : data.results;
}

export async function getModel(id: number): Promise<ACModelDetail> {
  return apiFetch<ACModelDetail>(`/v2/models/${id}/`);
}

export async function getModelBySlug(slug: string): Promise<ACModelDetail> {
  return apiFetch<ACModelDetail>(`/v2/models/by-slug/${slug}/`);
}

export async function getArchivedModels(): Promise<ACModelSummary[]> {
  const data = await apiFetch<ACModelSummary[] | PaginatedResponse<ACModelSummary>>(
    "/v2/models/archive/",
  );
  return Array.isArray(data) ? data : data.results;
}

export async function getMethodology(): Promise<Methodology> {
  return apiFetch<Methodology>("/v2/methodology/");
}
