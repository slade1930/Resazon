from app.nutrition.estimator import estimate_macros


def test_estimate_returns_facts():
    facts = estimate_macros(["arroz", "pollo"], servings=2)
    assert facts.is_estimated is True
    assert facts.calories is not None and facts.calories > 0
    assert facts.source == "estimación heurística local"


def test_estimate_unknown_ingredient_falls_back():
    facts = estimate_macros(["ingrediente-desconocido-xyz"], servings=1)
    assert facts.calories > 0
