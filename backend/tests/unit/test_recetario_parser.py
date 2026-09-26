from app.rag.ingestion.recetario_parser import parse_recetario

SAMPLE = """\
ARROZ CON POLLO
Sección: Principales
Tiempo: 45 minutos
Porciones: 4
Productos: MAGGI® Sabor de Gallina

INGREDIENTES:
- 2 tazas de arroz
- 1 libra de pollo
- 1 cucharada de aceite

PREPARACIÓN:
1. Sofreír el pollo con un poco de aceite.
2. Agregar el arroz y el caldo MAGGI.

SANCOCHO DE GALLINA
Sección: Sopas
Tiempo: 60 minutos
Porciones: 6

INGREDIENTES:
- 1 gallina
- 3 mazorcas
- sal al gusto

PREPARACIÓN:
1. Hervir la gallina con las mazorcas.
"""


def test_parses_two_recipes():
    docs = parse_recetario(SAMPLE)
    assert len(docs) == 2
    assert docs[0].name == "ARROZ CON POLLO"
    assert docs[1].name == "SANCOCHO DE GALLINA"


def test_extracts_metadata_and_ingredients():
    docs = parse_recetario(SAMPLE)
    first = docs[0]
    assert first.preparation_time_minutes == 45
    assert first.servings == 4
    assert first.page_or_section == "Principales"
    assert first.nestle_products and "MAGGI® Sabor de Gallina" in first.nestle_products
    names = [i.name for i in first.ingredients]
    assert "arroz" in names
    assert "pollo" in names


def test_quantity_and_unit():
    docs = parse_recetario(SAMPLE)
    arroz = [i for i in docs[0].ingredients if i.name == "arroz"][0]
    assert arroz.quantity == "2"
    assert arroz.unit == "tazas"


def test_preparation_steps_collected():
    docs = parse_recetario(SAMPLE)
    text = docs[0].preparation_text
    assert "Sofreír el pollo" in text
    assert "Agregar el arroz" in text
