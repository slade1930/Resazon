"""La generación saludable reintenta UNA vez cuando Gemini devuelve JSON malformado."""

from types import SimpleNamespace

import pytest

from app.services.healthy_recipe_service import HealthyRecipeService

VALID_RECIPE = (
    '{"name": "Arroz con Pollo Fit", "ingredients": ['
    '{"name": "arroz", "quantity": "1 taza"}, {"name": "pollo", "quantity": "200 g"}], '
    '"steps": ["Cocinar"], "preparation_time_minutes": 30, "servings": 2, "tips": ["Poca sal"]}'
)


class FakeProvider:
    def __init__(self, first_bad=True):
        self.calls = 0
        self.first_bad = first_bad
        self.temperatures = []

    def generate_content_with_usage(self, prompt, temperature=0.7):
        self.calls += 1
        self.temperatures.append(temperature)
        if self.first_bad and self.calls == 1:
            return SimpleNamespace(data="esto no es json")
        return SimpleNamespace(data=VALID_RECIPE, model_used="fake", input_tokens=1, output_tokens=1)


def _service():
    return HealthyRecipeService.__new__(HealthyRecipeService)


def test_reintenta_una_vez_y_parsea():
    provider = FakeProvider(first_bad=True)
    service = _service()
    attempt, recipe = service._generate_with_retry(provider, "prompt")
    assert provider.calls == 2
    assert attempt.data == VALID_RECIPE
    assert recipe.name == "Arroz con Pollo Fit"
    assert provider.temperatures == [0.6, 0.3]


def test_sin_error_solo_llama_una_vez():
    provider = FakeProvider(first_bad=False)
    service = _service()
    attempt, recipe = service._generate_with_retry(provider, "prompt")
    assert provider.calls == 1
    assert recipe.name == "Arroz con Pollo Fit"
    assert provider.temperatures == [0.6]


def test_si_ambas_fallan_lanza_ai_response_error():
    class AlwaysBad(FakeProvider):
        def generate_content_with_usage(self, prompt, temperature=0.7):
            self.calls += 1
            return SimpleNamespace(data="no json nunca")

    from app.core.exceptions import AIResponseError

    service = _service()
    provider = AlwaysBad()
    with pytest.raises(AIResponseError):
        service._generate_with_retry(provider, "prompt")
    assert provider.calls == 2