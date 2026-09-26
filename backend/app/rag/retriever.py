"""Retriever: genera el embedding de la query y llama al VectorStore."""

import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.rag.domain import RetrievedRecipe

logger = logging.getLogger(__name__)


class Retriever:
    """Recuperación semántica: query → embedding → pgvector → documentos.

    Si la IA está desactivada (GEMINI_AI_ENABLED=false), cae a una búsqueda
    léxica local (nombres + ingredientes por ILIKE) sin llamar a Gemini.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self._embeddings = None
        from app.rag.vector_store import VectorStore

        self.store = VectorStore(db)

    @property
    def _embedding_client(self):
        if self._embeddings is None:
            from app.rag.embeddings.embedding_client import EmbeddingClient

            self._embeddings = EmbeddingClient()
        return self._embeddings

    def search(
        self,
        query_text: str,
        top_k: int | None = None,
        country: str = "Panamá",
        raw_terms: list[str] | None = None,
    ) -> list[RetrievedRecipe]:
        k = top_k or settings.RAG_TOP_K
        if not self._ai_available():
            logger.info("IA desactivada — búsqueda léxica local: %r", raw_terms or query_text)
            terms = raw_terms or [t.strip() for t in query_text.split(",") if t.strip()]
            return self.store.search_lexical(terms, top_k=k, country=country)
        try:
            query_embedding = self._embedding_client.embed(query_text)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Embedding de query falló (%s) — búsqueda léxica local", exc)
            terms = raw_terms or [t.strip() for t in query_text.split(",") if t.strip()]
            return self.store.search_lexical(terms, top_k=k, country=country)
        return self.store.search(query_embedding, top_k=k, country=country)

    @staticmethod
    def _ai_available() -> bool:
        from app.ai.gemini_client import ai_available

        return ai_available()

    def build_query(self, ingredients: list[str], mode: str) -> str:
        joined = ", ".join(ingredients)
        if mode == "healthy":
            return f"versión saludable de recetas panameñas con {joined}"
        if mode == "generated":
            return f"platos con estilo panameño que usen {joined}"
        return f"recetas panameñas que usen: {joined}"
