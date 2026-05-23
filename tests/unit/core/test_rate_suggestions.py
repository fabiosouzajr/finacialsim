from decimal import Decimal

from app.core.rate_suggestions import RateCurvePoint, suggest_rate

CURVA_DEFAULT = [
    RateCurvePoint(ate_meses=24, taxa_mensal=Decimal("0.0149")),
    RateCurvePoint(ate_meses=36, taxa_mensal=Decimal("0.0169")),
    RateCurvePoint(ate_meses=48, taxa_mensal=Decimal("0.0189")),
    RateCurvePoint(ate_meses=60, taxa_mensal=Decimal("0.0199")),
    RateCurvePoint(ate_meses=72, taxa_mensal=Decimal("0.0219")),
]


def test_suggest_within_first_band() -> None:
    assert suggest_rate(12, CURVA_DEFAULT) == Decimal("0.0149")
    assert suggest_rate(24, CURVA_DEFAULT) == Decimal("0.0149")


def test_suggest_within_third_band() -> None:
    assert suggest_rate(48, CURVA_DEFAULT) == Decimal("0.0189")


def test_suggest_beyond_last_band_uses_last() -> None:
    assert suggest_rate(96, CURVA_DEFAULT) == Decimal("0.0219")
