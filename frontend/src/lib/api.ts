import {
  ACModelDetail,
  ACModelSummary,
  BrandOption,
  Methodology,
  Review,
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

export interface PageContent {
  slug: string;
  title_ru: string;
  content_ru: string;
}

export async function getPage(slug: string): Promise<PageContent> {
  return apiFetch<PageContent>(`/v2/pages/${slug}/`);
}

// Reviews
export async function getReviews(modelId: number): Promise<Review[]> {
  // Список без пагинации; на всякий случай поддерживаем оба формата.
  const data = await apiFetch<Review[] | PaginatedResponse<Review>>(
    `/v2/models/${modelId}/reviews/`,
  );
  return Array.isArray(data) ? data : data.results;
}

export interface ReviewCreatePayload {
  model: number;
  author_name: string;
  rating: number;
  pros?: string;
  cons?: string;
  comment?: string;
  /** Honeypot: должно остаться пустым. */
  website?: string;
}

// Brands (for submission form)
export async function getBrands(): Promise<BrandOption[]> {
  return apiFetch<BrandOption[]>("/v2/brands/");
}

// Submissions
export async function createSubmission(
  data: Record<string, string | number | boolean>,
  photos: File[],
): Promise<void> {
  const formData = new FormData();
  for (const [key, value] of Object.entries(data)) {
    if (value !== undefined && value !== null && value !== "") {
      formData.append(key, String(value));
    }
  }
  for (const photo of photos) {
    formData.append("photos", photo);
  }
  const res = await fetch(`${API_BASE}/v2/submissions/`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    let msg = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      msg = typeof body === "string" ? body : JSON.stringify(body);
    } catch {}
    throw new ApiError(res.status, msg);
  }
}

export async function createReview(payload: ReviewCreatePayload): Promise<Review> {
  const res = await fetch(`${API_BASE}/v2/reviews/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    let msg = `${res.status} ${res.statusText}`;
    try {
      const data = await res.json();
      msg = typeof data === "string" ? data : JSON.stringify(data);
    } catch {}
    throw new ApiError(res.status, msg);
  }
  return (await res.json()) as Review;
}
