"""Parser del "ReSazón Loop recetario ampliado" (Recetas Nestlé CAM).

Soporta los dos formatos del archivo:

1) Recetas numeradas (1. Nombre):
    1. Tamales Panameños

    País: Panamá
    Categoría: Plato tradicional
    Porciones: 12
    Productos Nestlé: Caldo de Pollo y Achiote MAGGI®, Pasta de Tomate MAGGI®

    Ingredientes

    -   5 lb de maíz pilado
    ...

    Preparación

    1.  Remojar el maíz...
    ...

    Nutrición de la fuente por porción: 471.8 kcal, 33.1 g proteína, ...

2) Recetas de los anexos (RECETA A01 - TÍTULO / POSTRE C01 - TÍTULO),
   con metadatos en mayúsculas cuyo valor va en la línea siguiente:
    RECETA A01 - RASPADO PANAMEÑO

    PAÍS:
    Panamá
    CATEGORÍA:
    Postre / bebida fría
    DIFICULTAD:
    Fácil
    TIEMPO:
    5 minutos aproximadamente
    PRODUCTO NESTLÉ:
    LA LECHERA® o producto dulce de la línea disponible
    INGREDIENTES:
    - Hielo triturado
    PREPARACIÓN:
    1. Triturar el hielo.

Se ignoran los bloques no-receta (METADATOS PARA RAG, REGLA DE RESAZÓN
LOOP, FUENTES, PROPÓSITO, IMPORTANTE PARA EL RAG, CLASIFICACIÓN, REGLA
PARA LA IA, FUENTES DE REFERENCIA). Los enlaces de "FUENTES" se mapean
por nombre a cada receta numerada.
"""

import re
import unicodedata

from app.rag.domain import ParsedNutrition, RecipeDocument
from app.rag.ingestion.recetario_parser import _TIME_RE, _parse_ingredient_line

_SOURCE = "Recetas Nestlé CAM · ReSazón Loop ampliado"

# ── Detección de bloques y metadatos ────────────────────────────────
_NUMBERED_TITLE_RE = re.compile(r"^(\d+)\s*\.\s+(.+)$")
_ANEXO_TITLE_RE = re.compile(r"^(?:RECETA|POSTRE)\s+([A-C])\s*\d{2}\s*-\s*(.+)$", re.IGNORECASE)
_METADATA_RE = re.compile(r"^([A-Za-zÁÉÍÓÚÑáéíóúñ ]+?)\s*:\s*(.*)$")

_SECTION_MARKERS = {
    "ingredientes": "ingredients",
    "ingrediente": "ingredients",
    "preparacion": "preparation",
    "preparación": "preparation",
}


def strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(c for c in normalized if unicodedata.category(c) != "Mn")


def _norm_key(key: str) -> str:
    return re.sub(r"\s+", " ", strip_accents(key).lower().rstrip(":").lstrip("1234567890.- )(").strip())


_METADATA_KEYS = {
    "pais": "country",
    "paises": "country",
    "categoria": "category",
    "categorias": "category",
    "porciones": "servings",
    "raciones": "servings",
    "producto nestle": "products",
    "productos nestle": "products",
    "producto nestle maggi": "products",
    "productos nestle maggi": "products",
    "dificultad": "difficulty",
    "tiempo": "time",
    "tiempo de preparacion": "time",
    "nutricion de la fuente por porcion": "nutrition",
    "contexto": "context",
    "nota": "note",
}

_NON_RECIPE_BLOCK_RE = re.compile(
    r"^(METADATOS PARA RAG|REGLA DE RESAZÓN LOOP|REGLA DE RESAZON LOOP|FUENTES\b|"
    r"FUENTES DE REFERENCIA|PROPÓSITO|PROPOSITO|IMPORTANTE PARA EL RAG|"
    r"CLASIFICACIÓN RECOMENDADA|CLASIFICACION RECOMENDADA|REGLA PARA LA IA|ANEXO\b)",
    re.IGNORECASE,
)
_SECTION_BANNER_RE = re.compile(r"^\s*([ABC])\s*\.\s+.*$", re.IGNORECASE)


# ── Nutrición de la fuente ──────────────────────────────────────────
def parse_nutrition(text: str) -> ParsedNutrition | None:
    """Extrae 'X kcal, Y g proteína, ...' a ParsedNutrition."""
    if not text or "kcal" not in text:
        return None
    patterns = {
        "protein_g": r"(?:prote(?:ína|ina)|protein)",
        "carbs_g": r"(?:carbohidratos|carbohidrato|carbohydrates|carbohydrate)",
        "fat_g": r"(?:grasas|grasa)",
        "fiber_g": r"fibra",
    }
    result: ParsedNutrition = ParsedNutrition()
    kcal = re.search(r"(\d+(?:\.\d+)?)\s*kcal", text, re.IGNORECASE)
    if kcal:
        result.calories = float(kcal.group(1))
    for field, pattern in patterns.items():
        sub = re.search(r"(\d+(?:\.\d+)?)\s*g\b(?: de)?\s*" + pattern, text, re.IGNORECASE)
        if sub:
            setattr(result, field, float(sub.group(1)))
    if all(v is None for v in (result.calories, result.protein_g, result.carbs_g, result.fat_g, result.fiber_g)):
        return None
    return result


def _normalize_difficulty(raw: str) -> str | None:
    if not raw:
        return None
    low = strip_accents(raw).lower()
    if "dificil" in low or "dificultad alta" in low:
        return "difícil"
    if "facil" in low:
        return "fácil"
    if "media" in low or "intermedia" in low or "mediana" in low:
        return "media"
    return low.strip()


_METADATA_TITLE_KEYS = {"pais", "categoria", "porciones", "raciones", "producto nestle", "productos nestle"}


def _is_new_numbered_recipe(lines: list[str], index: int) -> bool:
    """Título 'N. Nombre' si la línea no vacía siguiente es metadato de receta.

    Distingue '2. Guacho de Patitas de Pollo' (receta) de los pasos
    numerados ('2.  Sofreír...' / '1. Triturar el hielo.') que van
    seguidos de otra línea de paso, no de un metadato.
    """
    for look in range(index + 1, len(lines)):
        nxt = lines[look].strip()
        if not nxt:
            continue
        m = _METADATA_RE.match(nxt)
        if not m:
            return False
        return _norm_key(m.group(1)) in _METADATA_TITLE_KEYS
    return False


def parse_ampliado(text: str) -> list[RecipeDocument]:
    """Parsea el archivo completo del recetario ampliado."""
    source_links = _parse_source_links(text)
    documents: list[RecipeDocument] = []
    current: RecipeDocument | None = None
    section_key: str | None = None          # 'ingredients' | 'preparation' | None
    pending_key: str | None = None          # clave de metadato esperando continuación
    pending_lines: list[str] = []
    active_section = "N"                    # N (numeradas) | A | B | C
    lines = text.splitlines()

    def flush_pending() -> None:
        nonlocal pending_key, pending_lines
        if current is None:
            pending_key, pending_lines = None, []
            return
        value = "\n".join(pending_lines).strip()
        kind = _METADATA_KEYS.get(pending_key or "", "")
        _apply_metadata(current, kind, value)
        pending_key, pending_lines = None, []

    for index, raw in enumerate(lines):
        line = raw.strip()
        if not line:
            continue

        header = _SECTION_BANNER_RE.match(line)
        if header:
            active_section = header.group(1).upper()

        if _NON_RECIPE_BLOCK_RE.match(line):
            if current is not None:
                flush_pending()
                documents.append(current)
                current = None
            continue

        # ¿Nueva receta numerada? (solo si la siguiente línea es metadato).
        numbered = _NUMBERED_TITLE_RE.match(line)
        if numbered and _is_new_numbered_recipe(lines, index):
            flush_pending()
            if current is not None:
                documents.append(current)
            current = _new_document(numbered.group(2).strip(), active_section, source_links)
            current.page_or_section = f"Receta {numbered.group(1)}"
            section_key = None
            continue

        # ¿Nueva receta de anexo?
        anexo = _ANEXO_TITLE_RE.match(line)
        if anexo:
            flush_pending()
            if current is not None:
                documents.append(current)
            current = _new_document(anexo.group(2).strip(), active_section, source_links)
            current.page_or_section = f"RECETA {anexo.group(1)} - {anexo.group(2).strip()} ({active_section})"
            section_key = None
            continue

        if current is None:
            continue

        # Marcador de sección ('Ingredientes' / 'Preparación' / 'INGREDIENTES:').
        low = line.lower().lstrip("1234567890.- )(").rstrip(":.").strip()
        if low in _SECTION_MARKERS:
            flush_pending()
            section_key = _SECTION_MARKERS[low]
            continue

        # Metadato (clave: valor o clave: con valor en la línea siguiente).
        m = _METADATA_RE.match(line)
        if m:
            flush_pending()
            key = _norm_key(m.group(1))
            value = m.group(2).strip()
            if key not in _METADATA_KEYS and "nutricion" not in key and "porcion" not in key:
                # Línea tipo 'METADATOS PARA RAG' o ruido → no romper la receta.
                section_key = None
                continue
            section_key = None
            pending_key = key
            pending_lines = [value] if value else []
            continue

        if pending_key is not None:
            kind = _METADATA_KEYS.get(pending_key, "")
            if kind == "products" and line.startswith("-"):
                pending_lines.append(line.lstrip("- ").strip())
            elif _looks_like_filler(line) is False:
                pending_lines.append(line)
            continue

        if section_key == "ingredients":
            item = _parse_ingredient_line(line)
            if item:
                current.ingredients.append(item)
            continue

        if section_key == "preparation":
            step = _strip_step_number(line)
            current.preparation_text += (step or line) + "\n"
            continue

        current.raw_text += line + "\n"

    if current is not None:
        flush_pending()
        documents.append(current)

    for doc in documents:
        doc.preparation_text = "\n".join(
            p.strip() for p in doc.preparation_text.strip().splitlines() if p.strip()
        )
    return documents


def _new_document(name: str, active_section: str, source_links: dict[str, str]) -> RecipeDocument:
    doc = RecipeDocument(name=name.strip(), source=_SOURCE)
    doc.page_or_section = "Sección: " + active_section if active_section != "N" else None
    if active_section in ("A", "N"):
        doc.panama_verified = True
    else:
        doc.panama_verified = False
    if active_section == "B":
        doc.recipe_type = "SIMPLE"
    elif active_section == "C":
        doc.recipe_type = "POSTRE"
    link = _lookup_source_url(name, source_links)
    if link:
        doc.source_url = link
    return doc


def _apply_metadata(doc: RecipeDocument, kind: str, value: str) -> None:
    if not value:
        return
    if kind == "country":
        doc.country = value.strip()
    elif kind == "category":
        doc.category = value.strip()
    elif kind == "servings":
        found = _TIME_RE.search(value)
        if found:
            doc.servings = int(found.group(1))
    elif kind == "time":
        found = _TIME_RE.search(value)
        if found:
            doc.preparation_time_minutes = int(found.group(1))
    elif kind == "difficulty":
        doc.difficulty = _normalize_difficulty(value)
    elif kind == "nutrition":
        parsed = parse_nutrition(value)
        if parsed:
            doc.nutrition = parsed
    elif kind == "products":
        for part in re.split(r"[;,\n]", value):
            part = part.strip()
            if part and part not in doc.nestle_products:
                doc.nestle_products.append(part)
    elif kind in ("context", "note"):
        doc.raw_text += f"{kind.upper()}: {value}\n"


def _strip_step_number(line: str) -> str | None:
    m = re.match(r"^\s*\d+\s*[.)]\s*(.+)$", line)
    return m.group(1).strip() if m else None


def _looks_like_filler(line: str) -> bool:
    """¿La línea es un paso/ingrediente que no pertenece al metadato previo?"""
    low = line.lower().lstrip("1234567890.- )(").rstrip(":.").strip()
    if low in _SECTION_MARKERS:
        return True
    return _NUMBERED_TITLE_RE.match(line) is not None


# ── Fuentes ─────────────────────────────────────────────────────────
_FUENTES_NAME_RE = re.compile(r"^\s*[-*•]?\s*(.+?):\s*(https?://\S+)\s*$")
_CATEGORY_URL = (
    "https://www.recetasnestlecam.com/categorias/recetas-bien-panamenas"
)


def _parse_source_links(text: str) -> dict[str, str]:
    links: dict[str, str] = {}
    in_fuentes = False
    for line in text.splitlines():
        stripped = line.strip()
        if _NON_RECIPE_BLOCK_RE.match(stripped) and stripped.upper().startswith("FUENTES"):
            in_fuentes = True
            continue
        if in_fuentes:
            if stripped.startswith(("=", "---", "RECETA", "POSTRE")) or "======================================================" in stripped:
                break
            if _SECTION_BANNER_RE.search(stripped):
                break
            m = _FUENTES_NAME_RE.match(stripped)
            if m:
                links[m.group(1).strip()] = m.group(2).strip()
    return links


def _lookup_source_url(name: str, links: dict[str, str]) -> str | None:
    nf = strip_accents(name).lower()
    for label, url in links.items():
        lf = strip_accents(label).lower()
        if lf and (lf in nf or nf in lf):
            return url
    return None