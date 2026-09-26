import {
  ApiError,
  type ApiErrorBody,
  type GenerateResponse,
  type RecipeDetail,
  type RecipeListResponse,
  type RecipeSearchResponse,
  type ScanResponse,
} from "./types";

const BASE = "/api/v1";
const LANG_STORAGE_KEY = "rezazon.lang";

function currentLang(): string {
  if (typeof window === "undefined") return "es";
  const stored = localStorage.getItem(LANG_STORAGE_KEY);
  return stored === "en" || stored === "fr" ? stored : "es";
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = { ...(init?.headers as Record<string, string>) };
  if (init?.body && typeof init.body === "string") {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${BASE}${path}`, { ...init, headers });

  if (res.status === 204) return undefined as T;

  let body: unknown = null;
  try {
    body = await res.json();
  } catch {
    /* respuesta no JSON */
  }

  if (!res.ok) {
    const err = (body as ApiErrorBody) ?? {
      code: "http_error",
      message: `Upstream devolvió ${res.status}`,
      details: null,
    };
    throw new ApiError(res.status, err);
  }

  // El backend envuelve todo en {"data": ...}
  const data = (body as { data: T })?.data;
  return data as T;
}

export const api = {
  health: () => request<{ status: string }>("/health"),

  searchRecipes: (ingredients: string[], scanId?: number) =>
    request<RecipeSearchResponse>(
      `/recipes/search?lang=${currentLang()}`,
      { method: "POST", body: JSON.stringify({ ingredients, scan_id: scanId }) },
    ),

  listRecipes: (page = 1, pageSize = 20) =>
    request<RecipeListResponse>(`/recipes?lang=${currentLang()}&page=${page}&page_size=${pageSize}`),

  getRecipe: (id: number | string) => request<RecipeDetail>(`/recipes/${id}?lang=${currentLang()}`),

  generate: (ingredients: string[], dietaryGoal: string | null = null) =>
    request<GenerateResponse>(
      "/recipes/generate",
      { method: "POST", body: JSON.stringify({ ingredients, dietary_goal: dietaryGoal }) },
    ),

  healthy: (ingredients: string[]) =>
    request<GenerateResponse>(
      "/recipes/healthy",
      { method: "POST", body: JSON.stringify({ ingredients }) },
    ),

  scan: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<ScanResponse>("/scan", { method: "POST", body: form });
  },
};