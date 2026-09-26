export interface RecipeSummary {
  id: number | null;
  name: string;
  category: string | null;
  match_percentage: number;
  available_ingredients: string[];
  missing_ingredients: string[];
  preparation_time_minutes: number | null;
  servings: number;
  source: string;
  type: string;
  nestle_products: string[];
  difficulty: string | null;
  panama_verified: boolean;
}

export interface RecipeSearchResponse {
  recipes: RecipeSummary[];
  total: number;
}

export interface RecipeIngredient {
  name: string;
  quantity: string | null;
  unit: string | null;
  is_optional: boolean;
}

export interface NutritionFacts {
  calories: number | null;
  protein_g: number | null;
  carbs_g: number | null;
  fat_g: number | null;
  fiber_g: number | null;
  per_serving: boolean;
  is_estimated: boolean;
  source: string | null;
  disclaimer: string | null;
}

export interface RecipeDetail {
  name: string;
  category: string | null;
  ingredients: RecipeIngredient[];
  steps: string[];
  preparation_time_minutes: number | null;
  servings: number;
  type: string;
  source: string;
  description: string | null;
  nutrition: NutritionFacts | null;
  nestle_products: string[];
  difficulty: string | null;
  panama_verified: boolean;
  source_url: string | null;
  health_notes?: string[]; // Tips de recetas saludables (opcional, del backend)
}

export interface GenerateResponse {
  recipe: RecipeDetail;
}

export interface DetectedIngredient {
  name: string;
  confidence: number;
}

export interface ScanResponse {
  scan_id: number;
  detected_ingredients: DetectedIngredient[];
  traditional_recipes: RecipeSummary[];
}

export interface HealthyRecipeDetail {
  recipe_name: string;
  servings: number;
  ingredients: RecipeIngredient[];
  steps: string[];
  preparation_time_minutes: number;
  nutrition: {
    calories: number | null;
    protein_g: number | null;
    carbs_g: number | null;
    fat_g: number | null;
    fiber_g: number | null;
  };
  health_notes: string[];
}

export interface PaginationMeta {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface RecipeListResponse {
  items: RecipeSummary[];
  meta: PaginationMeta;
}

export interface RagResult {
  recipe_id: number;
  name: string;
  score: number;
  chunk_text: string;
}

export interface RagSearchResponse {
  results: RagResult[];
}

export interface ApiErrorBody {
  code: string;
  message: string;
  details: unknown;
}

export class ApiError extends Error {
  code: string;
  status: number;
  details: unknown;

  constructor(status: number, body: ApiErrorBody) {
    super(body.message);
    this.name = "ApiError";
    this.code = body.code;
    this.status = status;
    this.details = body.details;
  }
}