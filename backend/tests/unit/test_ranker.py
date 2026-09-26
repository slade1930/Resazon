from app.recipes.ranker import rank
from app.schemas.recipe import RecipeSummary


def _summary(name, pct, available, missing):
    return RecipeSummary(
        name=name,
        match_percentage=pct,
        available_ingredients=available,
        missing_ingredients=missing,
        source="test",
    )


def test_rank_by_percentage():
    a = _summary("a", 100.0, ["x"], [])
    b = _summary("b", 50.0, ["y"], [])
    c = _summary("c", 75.0, ["z"], [])
    result = rank([a, b, c])
    assert [r.name for r in result] == ["a", "c", "b"]


def test_rank_break_fewer_missing():
    a = _summary("a", 100.0, ["x"], ["faltante"])
    b = _summary("b", 100.0, ["x"], [])
    result = rank([a, b])
    assert result[0].name == "b"
