from datetime import date
from decimal import Decimal

from app.utils.br_format import format_brl, format_date_br, format_pct, parse_brl


def test_format_brl_thousand_separator():
    assert format_brl(Decimal("1234567.89")) == "R$ 1.234.567,89"


def test_format_brl_negative():
    assert format_brl(Decimal("-100.50")) == "-R$ 100,50"


def test_parse_brl_roundtrip():
    s = format_brl(Decimal("12345.67"))
    assert parse_brl(s) == Decimal("12345.67")


def test_format_pct():
    assert format_pct(Decimal("0.0189")) == "1,89%"


def test_format_date_br():
    assert format_date_br(date(2026, 5, 23)) == "23/05/2026"