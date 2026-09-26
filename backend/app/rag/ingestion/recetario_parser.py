"""Parser tolerante del recetario .txt a RecipeDocument.

Formato asumido (tolerante a variaciones):
  Título de la receta
  (opcional) Categoría: X | Sección: X | Tiempo: 30 minutos | Porciones: 4 | Productos: MAGGI®
  INGREDIENTES:
  - 2 tazas de arroz
  - 1 cucharada de aceite
  PREPARACIÓN:
  1. Paso uno...
  2. Paso dos...

El parser detecta títulos por heurística (línea sin puntuación al final,
en MAYÚSCULAS o precedida de línea en blanco) y clasifica el resto por
sección. Diseñado para ajustarse rápido al formato real del archivo.
"""

import re

from app.rag.domain import IngredientRef, RecipeDocument

_SECTION_MARKERS = {
    "ingredientes": "ingredients",
    "ingredienti": "ingredients",
    "preparacion": "preparation",
    "preparación": "preparation",
    "elaboracion": "preparation",
    "elaboración": "preparation",
    "productos": "products",
    "producto": "products",
    "ingredientes y preparacion": "both",
}

_METADATA_KEYS = {
    "tiempo": "time",
    "tiempo de preparacion": "time",
    "tiempo de preparación": "time",
    "porciones": "servings",
    "raciones": "servings",
    "categoria": "category",
    "categoría": "category",
    "seccion": "section",
    "sección": "section",
    "productos": "products",
    "producto": "products",
}

_QUANTITY_KEYWORDS = {
    "una",
    "un",
    "dos",
    "tres",
    "cuatro",
    "cinco",
    "media",
    "medio",
    "1/2",
    "1/4",
    "3/4",
    "1/3",
    "2/3",
    "1/8",
    "al gusto",
}

_UNIT_KEYWORDS = {
    "taza",
    "tazas",
    "cucharada",
    "cucharadas",
    "cucharadita",
    "cucharaditas",
    "libra",
    "libras",
    "lb",
    "kg",
    "g",
    "ml",
    "l",
    "unidad",
    "unidades",
    "pizca",
    "pizcas",
    "bote",
    "lata",
    "ramo",
    "ramitos",
    "hoja",
    "hojas",
    "diente",
    "dientes",
    "rajas",
    "rebanada",
    "rebanadas",
    "trozos",
    "piezas",
    "paquete",
    "caja",
    "sobre",
    "frasco",
    "cdita",
    "cdas",
    "cda",
    "litro",
    "litros",
    "cubito",
    "cubitos",
}

_TITLE_SECTION_PREAMBLE_RE = re.compile(r"^\s*(?:#+|[=\-*+]{2,})\s*")
_ALL_CAPS_RE = re.compile(r"^[^a-záéíóúñç]+$")
_NO_PUNCT_END_RE = re.compile(r"[.!?;:]$")
_METADATA_RE = re.compile(r"^([A-Za-zÁÉÍÓÚÑáéíóúñ ]+?)\s*:\s*(.+)$")
_TIME_RE = re.compile(r"(\d+)")
_NUMERED_STEP_RE = re.compile(r"^\s*\d+\s*[.)]\s*(.+)$")
_TRAILING_NUM_RE = re.compile(r"\s+\d+\s*$")
# Cantidad: entero, fracción, número mixto ("1 1/2") o fracción vulgar (½ ¼ ¾).
_QTY_LEADING_RE = re.compile(
    r"^(?P<qty>(?:\d+\s+)?\d+(?:/\d+)?|[½¼¾⅓⅔]+|\d*[½¼¾⅓⅔]?|[a-z]+)\s+(?P<rest>.+)$",
    re.IGNORECASE,
)

# Marcadores de página del recetario: "=== PÁGINA 3 ==="
_PAGE_RE = re.compile(r"^\s*=+\s*PÁGINA\s+(\d+)\s*=+\s*$", re.IGNORECASE | re.MULTILINE)

# Título duplicado consecutivo (ej. "arroz con pollo" x2 en cada página de receta).
_DUP_TITLE_RE = re.compile(r"^[a-záéíóúñàâãå' ]{3,50}$", re.IGNORECASE)


def _has_vulgar_fraction(s: str) -> bool:
    return any(ch in s for ch in "½¼¾⅓⅔")


def _classify_section(line: str) -> str | None:
    key = line.lower().strip().rstrip(":.,")
    return _SECTION_MARKERS.get(key)


def _parse_ingredient_line(line: str) -> IngredientRef | None:
    """Extrae quantity/unit/name de una línea tipo '- 2 tazas de arroz'."""
    raw = line.strip().lstrip("-*•·").strip()
    if not raw:
        return None

    optional = False
    if raw.lower().startswith("(opcional)") or "opcional" in raw.lower():
        optional = True
        raw = raw.replace("(opcional)", "").replace("opcional", "").strip(" ,-")

    quantity: str | None = None
    unit: str | None = None
    name = raw
    rest: str | None = None

    m = _QTY_LEADING_RE.match(raw)
    if m:
        maybe_qty = m.group("qty").lower()
        if (
            maybe_qty in _QUANTITY_KEYWORDS
            or any(c.isdigit() for c in maybe_qty)
            or _has_vulgar_fraction(maybe_qty)
        ):
            quantity = maybe_qty
            rest = m.group("rest")

    if rest:
        parts = rest.split(" ", 1)
        if parts[0].lower() in _UNIT_KEYWORDS:
            unit = parts[0]
            name = parts[1] if len(parts) > 1 else ""
        else:
            name = rest

    # Elimina el "de" conector ("2 tazas de arroz" → "arroz").
    name = re.sub(r"^(de|desde)\s+", "", name.strip())
    name = name.strip(" ,-")
    if not name:
        name = raw
    return IngredientRef(name=name, quantity=quantity, unit=unit, is_optional=optional)


def _parse_metadata(line: str, doc: RecipeDocument) -> bool:
    m = _METADATA_RE.match(line.strip())
    if not m:
        return False
    key = m.group(1).strip().lower()
    value = m.group(2).strip()
    kind = _METADATA_KEYS.get(key) or _METADATA_KEYS.get(key.rstrip("s"))
    if kind == "time":
        found = _TIME_RE.search(value)
        if found:
            doc.preparation_time_minutes = int(found.group(1))
    elif kind == "servings":
        found = _TIME_RE.search(value)
        if found:
            doc.servings = int(found.group(1))
    elif kind == "category":
        doc.category = value
    elif kind == "section":
        doc.page_or_section = value
    elif kind == "products":
        doc.nestle_products.extend(
            [p.strip() for p in value.replace(";", ",").split(",") if p.strip()]
        )
    return True


def _looks_like_title(line: str, prev_blank: bool) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if len(stripped) > 80 or len(stripped) < 3:
        return False
    if _NO_PUNCT_END_RE.search(stripped):
        return False
    if _NUMERED_STEP_RE.match(stripped):
        return False
    if stripped.startswith(("-", "*", "•")):
        return False
    # Línea de metadatos (contiene ':') no es título.
    if stripped.count(":") > 0:
        return False
    # Palabras de cantidad al inicio -> ingrediente (evita '2 tazas de arroz').
    first = stripped.split(" ", 1)[0].lower()
    if first in _QUANTITY_KEYWORDS:
        return False
    if all(c.isdigit() for c in first):
        return False
    return prev_blank or bool(_ALL_CAPS_RE.match(stripped)) or stripped.isupper()


def _title_from_duplicate(lines: list[str]) -> str | None:
    """Primer par de líneas consecutivas idénticas que parezca un título."""
    prev: str | None = None
    for line in lines:
        stripped = line.strip()
        if not stripped:
            prev = None
            continue
        if _DUP_TITLE_RE.match(stripped) and stripped == prev:
            return stripped
        prev = stripped
    return None


def _parse_page_recipe(content: str, page_num: int) -> RecipeDocument | None:
    """Extrae la receta de una página (pasos + ingredientes + título duplicado)."""
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    steps: list[str] = []
    ingredients: list[IngredientRef] = []

    for line in lines:
        step_match = _NUMERED_STEP_RE.match(line)
        if step_match:
            steps.append(step_match.group(1).strip())
            continue
        if line.startswith(("-", "*", "•")):
            item = _parse_ingredient_line(line)
            if item:
                ingredients.append(item)
            continue

    if not steps and not ingredients:
        return None  # página narrativa ("el sancocho de Nathalie")

    title = _title_from_duplicate(lines) or f"Página {page_num}"

    doc = RecipeDocument(name=title.title(), page_or_section=f"Página {page_num}")
    doc.ingredients = ingredients
    doc.preparation_text = "\n".join(steps)
    return doc


def _parse_paged_recetario(text: str) -> list[RecipeDocument]:
    """Parser para el formato del PDF: bloques '=== PÁGINA N ==='."""
    parts = re.split(_PAGE_RE, text)
    pages: dict[int, str] = {}
    for i in range(1, len(parts) - 1, 2):
        pages[int(parts[i])] = parts[i + 1]

    documents: list[RecipeDocument] = []
    for page_num in sorted(pages):
        doc = _parse_page_recipe(pages[page_num], page_num)
        if doc:
            documents.append(doc)
    return documents


def parse_recetario(text: str) -> list[RecipeDocument]:
    """Parsea el texto completo del recetario a una lista de RecipeDocument.

    Detecta el formato por páginas ('=== PÁGINA N ===') del PDF estructurado;
    si no lo encuentra, usa la heurística genérica por secciones.
    """
    if _PAGE_RE.search(text):
        return _parse_paged_recetario(text)

    documents: list[RecipeDocument] = []
    current: RecipeDocument | None = None
    section: str | None = None
    prev_blank = True
    title_line_handled = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            prev_blank = True
            continue

        section_marker = _classify_section(line)
        if section_marker:
            section = section_marker
            prev_blank = False
            continue

        if current is None or _looks_like_title(line, prev_blank and not title_line_handled):
            current = RecipeDocument(name=_TITLE_SECTION_PREAMBLE_RE.sub("", line).strip(" :"))
            documents.append(current)
            section = None
            prev_blank = False
            title_line_handled = True
            continue

        title_line_handled = False

        # Metadata (fuera de secciones).
        if not section and _parse_metadata(line, current):
            prev_blank = False
            continue

        if section in (None, "ingredients", "both"):
            item = _parse_ingredient_line(line)
            if item and not _NUMERED_STEP_RE.match(line):
                current.ingredients.append(item)
                prev_blank = False
                continue

        if section in ("preparation", "both") or _NUMERED_STEP_RE.match(line):
            step_match = _NUMERED_STEP_RE.match(line)
            if step_match:
                current.preparation_text += step_match.group(1).strip() + "\n"
            else:
                current.preparation_text += line + "\n"
            prev_blank = False
            continue

        if section == "products":
            for part in line.replace(";", ",").split(","):
                part = part.strip()
                if part:
                    current.nestle_products.append(part)
            prev_blank = False
            continue

        # Línea suelta inesperada: la anexamos como texto libre de la receta.
        current.preparation_text += line + "\n"
        prev_blank = False

    for doc in documents:
        doc.preparation_text = doc.preparation_text.strip()
    return documents
