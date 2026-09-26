"""Tipos de datos compartidos para el pipeline RAG."""

from dataclasses import dataclass, field


@dataclass
class IngredientRef:
    name: str
    quantity: str | None = None
    unit: str | None = None
    is_optional: bool = False

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
            "is_optional": self.is_optional,
        }


@dataclass
class ParsedNutrition:
    """Nutrición declarada por la fuente (no estimada)."""

    calories: float | None = None
    protein_g: float | None = None
    carbs_g: float | None = None
    fat_g: float | None = None
    fiber_g: float | None = None
    per_serving: bool = True


@dataclass
class RecipeDocument:
    name: str
    ingredients: list[IngredientRef] = field(default_factory=list)
    preparation_text: str = ""
    category: str | None = None
    country: str = "Panamá"
    source: str = "Recetario Nuestro Sabor Panamá"
    nestle_products: list[str] = field(default_factory=list)
    page_or_section: str | None = None
    raw_text: str = ""
    preparation_time_minutes: int | None = None
    servings: int = 2
    difficulty: str | None = None
    panama_verified: bool = True
    source_url: str | None = None
    nutrition: "ParsedNutrition | None" = None
    keywords: list[str] = field(default_factory=list)
    recipe_type: str = "TRADITIONAL"


@dataclass
class RecipeChunk:
    document: RecipeDocument
    text: str
    chunk_index: int = 0

    @property
    def embedding_text(self) -> str:
        parts = [
            f"Receta: {self.document.name}",
            f"Categoría: {self.document.category or 'desconocida'}",
            f"País: {self.document.country}",
        ]
        if self.document.nestle_products:
            parts.append("Productos: " + ", ".join(self.document.nestle_products))
        parts.append(self.text)
        return "\n".join(parts)


@dataclass
class RetrievedRecipe:
    recipe_id: int
    name: str
    score: float
    chunk_text: str
