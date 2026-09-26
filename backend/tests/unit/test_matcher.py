from app.recipes.matcher import match


def test_full_match():
    result = match(["arroz", "pollo"], ["arroz", "pollo"])
    assert result.match_percentage == 100.0
    assert set(result.available_ingredients) == {"arroz", "pollo"}
    assert result.missing_ingredients == []


def test_partial_match():
    result = match(["arroz"], ["arroz", "pollo"])
    assert result.match_percentage == 50.0  # 1/2 de la receta cubierto
    assert result.available_ingredients == ["arroz"]
    assert result.missing_ingredients == ["pollo"]


def test_substring_match():
    result = match(["cebolla"], ["cebolla cortada finamente", "pollo"])
    assert result.match_percentage == 50.0
    assert result.available_ingredients == ["cebolla cortada finamente"]
    assert result.missing_ingredients == ["pollo"]


def test_no_match():
    result = match(["mango"], ["arroz", "pollo"])
    assert result.match_percentage == 0.0
    assert result.available_ingredients == []
    assert sorted(result.missing_ingredients) == ["arroz", "pollo"]


def test_fuzzy_synonym():
    result = match(["aji"], ["ají"])
    assert result.match_percentage == 100.0
    assert result.available_ingredients == ["ají"]


def test_returns_original_recipe_name():
    # "ñame pelado y en cubos" normaliza a "name"; debe mostrarse el nombre real.
    result = match(["ñame"], ["ñame pelado y en cubos"])
    assert result.available_ingredients == ["ñame pelado y en cubos"]
