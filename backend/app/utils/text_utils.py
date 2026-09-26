"""Utilidades de texto."""

import re


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9ñáéíóúü\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    return text


def clean_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()
