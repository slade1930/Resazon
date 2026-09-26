"""Almacenamiento vectorial sobre PostgreSQL + pgvector."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.recipe import RecipeEmbedding
from app.rag.domain import RetrievedRecipe


def _vector_literal(embedding: list[float]) -> str:
    return "[" + ",".join(repr(float(v)) for v in embedding) + "]"


class VectorStore:
    """Interfaz sobre pgvector: insertar, reemplazar y buscar embeddings."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def insert(
        self, recipe_id: int, chunk_text: str, chunk_index: int, embedding: list[float]
    ) -> RecipeEmbedding:
        row = RecipeEmbedding(
            recipe_id=recipe_id,
            chunk_text=chunk_text,
            chunk_index=chunk_index,
            embedding=embedding,
        )
        self.db.add(row)
        return row

    def replace_for_recipe(
        self, recipe_id: int, chunks: list[tuple[str, int]], embeddings: list[list[float]]
    ) -> int:
        """Borra los embeddings previos de una receta e inserta los nuevos (ingesta idempotente)."""
        self.db.query(RecipeEmbedding).filter(RecipeEmbedding.recipe_id == recipe_id).delete()
        for (text_chunk, index), emb in zip(chunks, embeddings, strict=False):
            self.insert(recipe_id, text_chunk, index, emb)
        self.db.flush()
        return len(chunks)

    def search(
        self,
        embedding: list[float],
        top_k: int = 5,
        country: str = "Panamá",
    ) -> list[RetrievedRecipe]:
        """Búsqueda por similitud coseno (distancia <=>)."""
        sql = text(
            """
            SELECT re.recipe_id, r.name, re.chunk_text,
                   (re.embedding <=> :embedding) AS distance
            FROM recipe_embeddings re
            JOIN recipes r ON r.id = re.recipe_id
            WHERE r.country = :country
            ORDER BY distance ASC
            LIMIT :top_k
            """
        )
        rows = self.db.execute(
            sql,
            {
                "embedding": _vector_literal(embedding),
                "country": country,
                "top_k": top_k,
            },
        ).mappings()
        return [
            RetrievedRecipe(
                recipe_id=row["recipe_id"],
                name=row["name"],
                score=1.0 - float(row["distance"]),
                chunk_text=row["chunk_text"],
            )
            for row in rows
        ]

    def search_lexical(
        self,
        terms: list[str],
        top_k: int = 5,
        country: str = "Panamá",
    ) -> list[RetrievedRecipe]:
        """Búsqueda sin IA: nombre, categoría, keywords y/o ingredientes por ILIKE.

        Cubre la bolsa multilingüe almacenada en `recipes.search_keywords`,
        el nombre, la categoría, el nombre original del ingrediente y la forma
        normalizada. Funciona con GEMINI_AI_ENABLED=false (cero llamadas a Gemini).
        """
        import unicodedata

        def norm(t: str) -> str:
            return unicodedata.normalize("NFKC", t.strip()).casefold()

        patterns = ["%" + norm(t) + "%" for t in terms if norm(t)]
        if not patterns:
            return []
        array_literal = "ARRAY[" + ",".join("'" + p.replace("'", "''") + "'" for p in patterns) + "]"
        sql = text(
            f"""
            SELECT r.id AS recipe_id, r.name,
                   COALESCE((r.name ILIKE ANY({array_literal}))::int, 0)
                   + COALESCE((r.category ILIKE ANY({array_literal}))::int, 0)
                   + COALESCE((r.search_keywords ILIKE ANY({array_literal}))::int, 0)
                   + COALESCE(
                       (
                       SELECT COUNT(DISTINCT i.normalized_name)
                       FROM recipe_ingredients ri
                       JOIN ingredients i ON i.id = ri.ingredient_id
                       WHERE ri.recipe_id = r.id
                         AND (
                               i.normalized_name ILIKE ANY({array_literal})
                               OR i.name ILIKE ANY({array_literal})
                             )
                       ), 0) AS score,
                   r.name AS chunk_text
            FROM recipes r
            WHERE r.country = :country
              AND (
                    r.name ILIKE ANY({array_literal})
                    OR r.category ILIKE ANY({array_literal})
                    OR r.search_keywords ILIKE ANY({array_literal})
                    OR EXISTS (
                        SELECT 1
                        FROM recipe_ingredients ri2
                        JOIN ingredients i2 ON i2.id = ri2.ingredient_id
                        WHERE ri2.recipe_id = r.id
                          AND (
                                i2.normalized_name ILIKE ANY({array_literal})
                                OR i2.name ILIKE ANY({array_literal})
                              )
                    )
              )
            ORDER BY score DESC, r.name ASC
            LIMIT :top_k
            """
        )
        rows = self.db.execute(
            sql,
            {"country": country, "top_k": top_k},
        ).mappings()
        return [
            RetrievedRecipe(
                recipe_id=row["recipe_id"],
                name=row["name"],
                score=float(row["score"]),
                chunk_text=row["chunk_text"],
            )
            for row in rows
        ]

    def count(self) -> int:
        return self.db.query(RecipeEmbedding).count()
