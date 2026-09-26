"""Cobertura del archivo de traducciones autorado (data/i18n.json)."""

import json
from pathlib import Path

from app.i18n import DEFAULT_LANG, SUPPORTED_LANGS

_DATA = Path(__file__).resolve().parents[2] / "data" / "i18n.json"
PAYLOAD = json.loads(_DATA.read_text(encoding="utf-8"))


def _assert_complete(section: str, spec: dict):
    targets = [code for code in SUPPORTED_LANGS if code != DEFAULT_LANG]
    for key, langs in spec.items():
        for lang in targets:
            value = langs.get(lang)
            assert value not in (None, ""), (
                f"{section}[{key!r}].{lang} vacío o ausente"
            )


def test_categories_complete():
    _assert_complete("categories", PAYLOAD["categories"])


def test_units_complete():
    _assert_complete("units", PAYLOAD["units"])


def test_ingredients_complete():
    _assert_complete("ingredients", PAYLOAD["ingredients"])


def test_recipes_complete_and_names_present():
    for recipe_id, langs in PAYLOAD["recipes"].items():
        for lang in SUPPORTED_LANGS:
            if lang == DEFAULT_LANG:
                continue
            entry = langs.get(lang)
            assert entry and entry.get("name"), (
                f"recipes[{recipe_id}].{lang} sin name"
            )
            assert entry.get("steps"), f"recipes[{recipe_id}].{lang} sin steps"


def test_recipes_count_matches_db():
    assert len(PAYLOAD["recipes"]) == 33
    assert len(PAYLOAD["ingredients"]) == 145
    assert len(PAYLOAD["units"]) == 21
    assert len(PAYLOAD["categories"]) == 15


def test_en_fr_names_differ_from_each_other():
    for recipe_id, langs in PAYLOAD["recipes"].items():
        en = langs["en"]["name"]
        fr = langs["fr"]["name"]
        assert en != fr, f"recipes[{recipe_id}] en==fr ({en})"