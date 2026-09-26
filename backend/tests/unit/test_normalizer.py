from app.vision.ingredient_normalizer import (
    normalize_ingredient,
    normalize_list,
    synonym_aliases_for,
)


def test_plural_singular():
    assert normalize_ingredient("huevos") == "huevo"
    assert normalize_ingredient("platanos") == "platano"


def test_synonyms():
    assert normalize_ingredient("aji") == "aji"
    assert normalize_ingredient("chiltoma") == "tomate"
    assert normalize_ingredient("culantro") == "culantro"


def test_strip_parenthesis():
    assert normalize_ingredient("arroz (blanco)") == "arroz"


def test_stopwords_removed():
    assert normalize_ingredient("sal al gusto") == ""


def test_normalize_list_dedupes():
    result = normalize_list(["huevo", "Huevos", "aji", "tomate"])
    assert result == ["huevo", "aji", "tomate"]


def test_english_synonyms():
    assert normalize_ingredient("chicken breast") == "pechuga de pollo"
    assert normalize_ingredient("rice") == "arroz"
    assert normalize_ingredient("potatoes") == "papa"
    assert normalize_ingredient("beans") == "frijol"
    assert normalize_ingredient("corn") == "maiz"


def test_french_synonyms():
    assert normalize_ingredient("poulet") == "pollo"
    assert normalize_ingredient("pommes de terre") == "papa"
    assert normalize_ingredient("fromage") == "queso"
    assert normalize_ingredient("lait évaporé") == "leche evaporada"
    assert normalize_ingredient("sucre") == "azucar"


def test_word_boundaries_prevent_false_hits():
    # "oil" no debe matchear "boiled" (± "boil water"), ni "sal" dentro de "salchicha".
    assert normalize_ingredient("boiled water") == "boiled water"
    assert normalize_ingredient("salchicha") == "salchicha"
    # El plural "tortillas de maíz" colapsa a la tortilla canónica.
    assert normalize_ingredient("tortillas") == "tortilla"


def test_synonym_aliases_for_includes_foreign_terms():
    aliases = synonym_aliases_for("pollo")
    assert "chicken" in aliases
    assert "poulet" in aliases
    assert "gallina" in aliases
