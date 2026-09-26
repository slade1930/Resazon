"""Centraliza el acceso a Gemini (generación, visión, embeddings)."""

from app.ai.gemini_client import GeminiClient, get_gemini_client

__all__ = ["GeminiClient", "get_gemini_client"]
