from pathlib import Path

from app.rag.ingestion.ampliado_parser import parse_ampliado, parse_nutrition

BACKEND_DIR = Path(__file__).resolve().parents[2]
AMPLIADO_FILE = BACKEND_DIR / "ReSazon_Loop_recetario_ampliado.txt"

SAMPLE = """\
--- METADATOS PARA RAG ---
Formato: recetario ampliado

--- FUENTES DE REFERENCIA ---
FUENTES:
- Corte de res: https://www.recetasnestlecam.com/recetas/corte-de-res
- Guacho de Patitas de Pollo: https://www.recetasnestlecam.com/recetas/guacho-de-patitas

1. Tamales Panameños
País: Panamá
Categoría: Plato principal
Porciones: 6
INGREDIENTES:
- 2 tazas de maíz pilado
- 1 galleta maría molida
PREPARACIÓN:
1.  Remojar el maíz desde la noche anterior.
2.  Moler el maíz hasta obtener una masa fina.
3.  Cocinar a fuego lento en una olla grande.

2. Guacho de Patitas de Pollo
País: Panamá
Categoría: Sopas
Porciones: 4
Dificultad: Media
INGREDIENTES:
- 1 libra de patitas de pollo
- 1 taza de arroz
PREPARACIÓN:
1.  Dorar las patitas de pollo.
2.  Cocinar con el arroz hasta que todo esté suave.
Nutrición de la fuente por porción:
471.8 kcal, 33.1 g proteína, 41.8 g carbohidratos, 18.4 g grasa, 5.2 g fibra.

--- A. RECETAS PANAMEÑAS SENCILLAS (Anexo A) ---
A. RECETAS PANAMEÑAS SENCILLAS
RECETA A01 - RASPADO PANAMEÑO
País: Panamá
Categoría: Postre
Porciones: 2
INGREDIENTES:
- 2 tazas de hielo triturado
- 1/2 taza de sirope de fresa
PREPARACIÓN:
1. Triturar el hielo.
2. Agregar el sirope y revolver.

--- B. RECETAS MUY SENCILLAS PARA EL CATÁLOGO GENERAL (B) ---
B. RECETAS MUY SENCILLAS PARA EL CATÁLOGO GENERAL
RECETA B01 - CHICHA DE AVENA
País: Panamá
Categoría: Bebida
Porciones: 4
INGREDIENTES:
- 2 tazas de avena
- 4 tazas de agua
- canela en polvo
PREPARACIÓN:
1. Mezclar todos los ingredientes.
2. Refrigerar por una hora.

--- C. POSTRES SENCILLOS (Anexo C) ---
C. POSTRES SENCILLOS
POSTRE C01 - MOUSSE DE MARACUYÁ
País: Panamá
Categoría: Postre
Porciones: 4
INGREDIENTES:
- 1 taza de pulpa de maracuyá
- 1 lata de leche condensada
- 1 taza de crema de leche
PREPARACIÓN:
1. Batir la crema hasta que esté firme.
2. Incorporar el maracuyá y la leche condensada.
"""


def test_parses_numbered_recipes_without_swallowing_next():
    docs = parse_ampliado(SAMPLE)
    names = [d.name for d in docs]
    # La receta 1 no lleva bloque de nutrición, así que la "2." siguiente debe
    # detectarse como receta nueva (regresión del lookahead).
    assert "Tamales Panameños" in names
    assert "Guacho de Patitas de Pollo" in names
    tamales = next(d for d in docs if d.name == "Tamales Panameños")
    prep = tamales.preparation_text
    assert "2. Guacho de Patitas de Pollo" not in prep
    assert "Cocinar a fuego lento" in prep


def test_nutrition_and_difficulty():
    guacho = next(d for d in parse_ampliado(SAMPLE) if d.name.startswith("Guacho"))
    assert guacho.nutrition is not None
    assert guacho.nutrition.calories == 471.8
    assert guacho.nutrition.protein_g == 33.1
    assert guacho.nutrition.carbs_g == 41.8
    assert guacho.nutrition.fat_g == 18.4
    assert guacho.difficulty == "media"


def test_anexos_sections_letter_and_types():
    docs = {d.name: d for d in parse_ampliado(SAMPLE)}
    raspado = docs["RASPADO PANAMEÑO"]
    assert raspado.panama_verified is True
    assert raspado.recipe_type == "TRADITIONAL"
    assert raspado.page_or_section and "RECETA A" in raspado.page_or_section and "(A)" in raspado.page_or_section

    chicha = docs["CHICHA DE AVENA"]
    assert chicha.panama_verified is False
    assert chicha.recipe_type == "SIMPLE"
    assert "(B)" in chicha.page_or_section

    mousse = docs["MOUSSE DE MARACUYÁ"]
    assert mousse.panama_verified is False
    assert mousse.recipe_type == "POSTRE"
    assert "(C)" in mousse.page_or_section


def test_anexo_single_space_steps_stay_in_recipe():
    mousse = next(d for d in parse_ampliado(SAMPLE) if d.name == "MOUSSE DE MARACUYÁ")
    assert "Batir la crema" in mousse.preparation_text
    assert "Incorporar el maracuyá" in mousse.preparation_text


def test_parse_nutrition_only_for_kcal_blocks():
    assert parse_nutrition("471.8 kcal, 33.1 g proteína, 41.8 g carbohidratos, 18.4 g grasa, 5.2 g fibra.") is not None
    assert parse_nutrition("aguas y harinas") is None


def test_full_file_parses_28_recipes():
    text = AMPLIADO_FILE.read_text(encoding="utf-8")
    docs = parse_ampliado(text)
    assert len(docs) == 28


def test_full_file_no_page_or_section_leak():
    text = AMPLIADO_FILE.read_text(encoding="utf-8")
    docs = parse_ampliado(text)
    for doc in docs:
        assert "---" not in doc.name