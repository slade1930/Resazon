"""Contractos de recetas (búsqueda, detalle, generación)."""

from pydantic import BaseModel, Field

from app.schemas.nutrition import NutritionFacts


class RecipeSearchRequest(BaseModel):
    ingredients: list[str] = Field(min_length=1)
    scan_id: int | None = None


class RecipeSummary(BaseModel):
    id: int | None = None
    name: str
    category: str | None = None
    match_percentage: float
    available_ingredients: list[str] = Field(default=list)
    missing_ingredients: list[str] = Field(default=list)
    preparation_time_minutes: int | None = None
    servings: int = 2
    source: str
    type: str = "traditional"
    difficulty: str | None = None
    panama_verified: bool = True
    nestle_products: list[str] = Field(default=list)


class RecipeSearchResponse(BaseModel):
    recipes: list[RecipeSummary]
    total: int = 0


class RecipeIngredientOut(BaseModel):
    name: str
    quantity: str | None = None
    unit: str | None = None
    is_optional: bool = False


class RecipeDetail(BaseModel):
    name: str
    category: str | None = None
    ingredients: list[RecipeIngredientOut]
    steps: list[str] = Field(default=list)
    preparation_time_minutes: int | None = None
    servings: int = 2
    type: str = "traditional"
    source: str
    difficulty: str | None = None
    panama_verified: bool = True
    source_url: str | None = None
    description: str | None = None
    nutrition: NutritionFacts | None = None
    nestle_products: list[str] = Field(default=list)
    health_notes: list[str] | None = None


class RecipeGenerateRequest(BaseModel):
    ingredients: list[str] = Field(min_length=1)
    dietary_goal: str | None = None


class RecipeGenerateResponse(BaseModel):
    recipe: RecipeDetail
