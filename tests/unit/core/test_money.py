from decimal import Decimal

from app.core.money import CENTAVO, PCT_DEC, TAXA_DEC, quantize_brl, to_decimal


def test_centavo_constant() -> None:
    assert Decimal("0.01") == CENTAVO


def test_quantize_brl_half_up() -> None:
    assert quantize_brl(Decimal("0.125")) == Decimal("0.13")
    assert quantize_brl(Decimal("0.124")) == Decimal("0.12")
    assert quantize_brl(Decimal("0.135")) == Decimal("0.14")


def test_quantize_brl_negatives() -> None:
    assert quantize_brl(Decimal("-0.125")) == Decimal("-0.13")


def test_to_decimal_accepts_str_int_float() -> None:
    assert to_decimal("10.50") == Decimal("10.50")
    assert to_decimal(10) == Decimal("10")
    assert to_decimal(10.5) == Decimal("10.5")


def test_pct_taxa_precisions() -> None:
    assert Decimal("0.0001") == PCT_DEC
    assert Decimal("0.00000001") == TAXA_DEC
