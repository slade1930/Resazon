"""Chunking selectivo de recetas largas para embeddings autocontenibles."""

from app.rag.domain import RecipeChunk, RecipeDocument

MAX_CHARS = 1400
OVERLAP_CHARS = 120


def chunk_recipe(document: RecipeDocument) -> list[RecipeChunk]:
    """Devuelve chunks autocontenibles de la receta.

    Si el texto es corto, un solo chunk. Si es largo, se fragmenta por
    párrafos con un solapamiento pequeño para no perder contexto.
    """
    chunks: list[RecipeChunk] = []
    if document.name:
        header = document.name
    else:
        header = ""

    if len(document.preparation_text) <= MAX_CHARS:
        text = (f"Receta {header}" + "\n\n" + document.preparation_text).strip()
        return [RecipeChunk(document=document, text=text, chunk_index=0)]

    paragraphs = [p.strip() for p in document.preparation_text.split("\n") if p.strip()]
    buffer = []
    current_len = 0
    index = 0

    def flush() -> None:
        nonlocal index
        body = "\n".join(buffer)
        text = (f"Receta {header}" + "\n\n" + body).strip()
        chunks.append(RecipeChunk(document=document, text=text, chunk_index=index))
        index += 1
        buffer.clear()

    for para in paragraphs:
        if current_len + len(para) > MAX_CHARS and buffer:
            flush()
            # overlapping tail: reusa el final del texto para no perder contexto
            last = buffer[-1] if buffer else ""
            if len(last) > OVERLAP_CHARS:
                buffer.append(last[-OVERLAP_CHARS:])
            current_len = sum(len(p) for p in buffer)
        buffer.append(para)
        current_len += len(para)

    if buffer:
        flush()

    return chunks
