"""Cliente de embeddings apoyado en el cliente único de Gemini."""

from app.ai.gemini_client import GeminiClient, gemini_client_provider


class EmbeddingClient:
    """Abstrae la generación de vectores; hoy usa Gemini, mañana puede ser local."""

    def __init__(self) -> None:
        self._client: GeminiClient = gemini_client_provider()

    def embed(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self._client.generate_embeddings(texts)
