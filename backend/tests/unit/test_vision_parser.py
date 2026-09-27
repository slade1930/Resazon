"""El parser de respuestas de Gemini Vision nunca debe lanzar ni devolver basura."""

import pytest

from app.ai.gemini_client import _parse_ingredients_response, _strip_code_fence


def test_estricto_valido():
    result = _parse_ingredients_response(
        '{"ingredients": [{"name": "leche condensada", "confidence": 0.99}]}'
    )
    assert result.ingredients[0].name == "leche condensada"
    assert result.ingredients[0].confidence == 0.99


def test_con_code_fence():
    result = _parse_ingredients_response(
        '```json\n{"ingredients": [{"name": "arroz", "confidence": 0.9}]}\n```'
    )
    assert result.ingredients[0].name == "arroz"


@pytest.mark.parametrize(
    "sucio",
    [
        '{"ingredientes": [{"nombre": "yuca", "confianza": 0.85}]}',
        '{"ingredients": [{"nombre": "plátano", "confianza": "0.8"}]}',
        '{"ingredients": [{"name": "pollo", "confidence": 1.5}]}',
        '{"items": ["huevo", "manteca"]}',
        '{"ingredients": [{"name": "camarón", "confidence": "alta"}]}',
    ],
)
def test_entradas_sucias_no_lanzan(sucio):
    result = _parse_ingredients_response(sucio)
    assert isinstance(result.ingredients, list)


def test_confidence_acotada():
    result = _parse_ingredients_response(
        '{"ingredients": [{"name": "pollo", "confidence": 1.5}, {"name": "arroz", "confidence": -1}]}'
    )
    confs = [d.confidence for d in result.ingredients]
    assert all(0.0 <= c <= 1.0 for c in confs)


@pytest.mark.parametrize(
    "inutilizable",
    [
        "",
        "no es json en absoluto",
        '{"otra_cosa": 123}',
        '{"ingredients": "ninguno"}',
        "[1, 2, 3]",
    ],
)
def test_respuesta_inutilizable_devuelve_vacio(inutilizable):
    assert _parse_ingredients_response(inutilizable).ingredients == []


def test_strip_code_fence():
    assert _strip_code_fence("```json\n{\"a\": 1}\n```") == '{"a": 1}'