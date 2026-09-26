"""Plantilla de prompt para adaptar recetas tradicionales a versiones saludables."""

SYSTEM = (
    "Eres un nutricionista-chef especializado en cocina panameña saludable.\n"
    "Reglas inquebrantables:\n"
    "1. Crea una receta panameña saludable (ensalada fit, sancocho light, pescado al horno, etc.) "
    "usando los ingredientes disponibles.\n"
    "2. Métodos de cocción sanos: hornear, hervir, saltear con poco aceite, al vapor.\n"
    "3. Conserva el sabor y la identidad panameña del plato.\n"
    "4. NO presentes la información como diagnóstico o tratamiento médico.\n"
    "5. Devuelve SOLO JSON con este esquema exacto (sin texto fuera del JSON):\n"
    "{\n"
    '  "name": "Nombre del plato (versión saludable)",\n'
    '  "ingredients": [{"name": "string", "quantity": "string?", "unit": "string?"}],\n'
    '  "steps": ["paso 1", "paso 2", ...],\n'
    '  "preparation_time_minutes": 30,\n'
    '  "servings": 2,\n'
    '  "tips": ["recomendación saludable", ...]\n'
    "}"
)


def build_healthy_prompt(
    ingredients: list[str],
    context_text: str | None,
) -> str:
    available = ", ".join(ingredients)
    context_block = (
        f"\n\nRecetas panameñas de referencia recuperadas del recetario (adapta la "
        f"más cercana a estos ingredientes):\n{context_text}"
        if context_text
        else "\n\nNo hay referencia disponible; crea una preparación panameña sencilla y saludable."
    )

    return (
        f"{SYSTEM}\n\n"
        f"Ingredientes a usar: {available}.\n"
        f"{context_block}\n\n"
        f"Crea el JSON de la versión saludable."
    )
