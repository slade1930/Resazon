"""Helpers de localización del contenido (app.i18n) — sin BD."""

from app.i18n import (
    DEFAULT_LANG,
    SUPPORTED_LANGS,
    ingredient_name,
    normalize_lang,
    recipe_category,
    recipe_name,
    recipe_steps,
    unit_name,
)


class _Translation:
    def __init__(self, lang, name=None, category=None, steps=None):
        self.lang = lang
        self.name = name
        self.category = category
        self.steps = steps


def _recipe(name="Arroz con leche", category="Postre", translations=()):
    return type("R", (), {"name": name, "category": category, "translations": list(translations)})()


def _ingredient(name="harina", translations=()):
    return type("I", (), {"name": name, "translations": list(translations)})()


def test_normalize_lang():
    assert normalize_lang("en") == "en"
    assert normalize_lang("FR") == DEFAULT_LANG
    assert normalize_lang("xx") == DEFAULT_LANG
    assert normalize_lang(None) == DEFAULT_LANG
    assert normalize_lang("") == DEFAULT_LANG


def test_supported_langs():
    assert SUPPORTED_LANGS == ("es", "en", "fr")


def test_recipe_name_falls_back_to_es():
    recipe = _recipe()
    assert recipe_name(recipe, None) == "Arroz con leche"
    assert recipe_name(recipe, "xx") == "Arroz con leche"


def test_recipe_name_uses_translation():
    recipe = _recipe(translations=[_Translation("en", name="Rice pudding")])
    assert recipe_name(recipe, "en") == "Rice pudding"
    assert recipe_name(recipe, "fr") == "Arroz con leche"


def test_recipe_category_and_steps():
    recipe = _recipe(
        translations=[
            _Translation("fr", category="Dessert", steps=["Mélanger", "Cuire"])
        ]
    )
    assert recipe_category(recipe, "fr") == "Dessert"
    assert recipe_category(recipe, "en") == "Postre"
    assert recipe_steps(recipe, "fr") == ["Mélanger", "Cuire"]
    assert recipe_steps(recipe, "en") == []


def test_ingredient_name_resolution():
    ingredient = _ingredient(translations=[_Translation("en", name="flour"), _Translation("fr", name="farine")])
    assert ingredient_name(ingredient, "en") == "flour"
    assert ingredient_name(ingredient, "fr") == "farine"
    assert ingredient_name(ingredient, None) == "harina"
    assert ingredient_name(_ingredient(), "en") == "harina"


def test_unit_name_resolution():
    assert unit_name("tazas", "en") == "cups"
    assert unit_name("tazas", "fr") == "tasses"
    assert unit_name("tazas", None) == "tazas"
    assert unit_name(None, "en") is None
    assert unit_name("tazas", "xx") == "tazas"
    # unidad fuera del mapa se conserva
    assert unit_name("apio", "en") == "apio"


def test_units_map_has_all_data_keys():
    from app.i18n import UNITS
    from tests.unit.test_i18n_data import PAYLOAD

    for key, langs in PAYLOAD["units"].items():
        for lang in ("en", "fr"):
            assert langs[lang] == UNITS[key][lang], f"unit {key!r}.{lang} fuera de sync"