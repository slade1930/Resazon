"""Plantilla de prompt para el modo "Crear con mis ingredientes"."""

CONTEXT_STYLE_MARKER = "[CONTEXTO_PANAMENO - solo como guía de estilo, no para copiar]"

SYSTEM = (
    "Eres un chef panameño. Crea recetas sencillas, prácticas y con sabor panameño "
    "usando los ingredientes que el usuario ya tiene. Reglas inquebrantables:\n"
    "1. Prioriza los ingredientes disponibles; minimiza los ingredientes adicionales.\n"
    "2. Mantén identidad panameña (técnicas, combinaciones, nombres de platos).\n"
    "3. Devuelve SOLO JSON con este esquema exacto (sin texto fuera del JSON):\n"
    "{\n"
    '  "name": "Nombre del plato",\n'
    '  "ingredients": [{"name": "string", "quantity": "string?", "unit": "string?"}],\n'
    '  "steps": ["paso 1", "paso 2", ...],\n'
    '  "preparation_time_minutes": 30,\n'
    '  "servings": 2,\n'
    '  "tips": ["consejo 1", ...]\n'
    "}\n"
    "4. El campo `name` no debe repetir el título de ninguna receta del contexto.\n"
    "5. No inventes marcas comerciales."
)


def build_generation_prompt(
    ingredients: list[str],
    context_text: str | None,
) -> str:
    available = ", ".join(ingredients)
    context_block = (
        f"\n\n{CONTEXT_STYLE_MARKER}\nReferencias recuperadas del recetario panameño "
        "(úsalas solo para captar estilo, técnicas y nombres locales):\n{context_text}"
        if context_text
        else "\n\nNo hay contexto panameño disponible. Usa tu conocimiento de cocina panameña."
    )

    return (
        f"{SYSTEM}\n\n"
        f"Ingredientes disponibles: {available}.\n"
        f"{context_block}\n\n"
        f"Genera UNA receta panameña que use la mayor cantidad posible de esos "
        f"ingredientes. Respeta el esquema JSON."
    )
