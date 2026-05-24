from decimal import Decimal

from app.integrations.bacen.conversions import anual_para_mensal, mensal_para_anual


def test_mensal_to_anual_roundtrip():
    m = Decimal("0.015")
    a = mensal_para_anual(m)
    back = anual_para_mensal(a)
    assert abs(back - m) < Decimal("0.000001")


def test_one_pct_mensal_approx_12_68_pct_anual():
    a = mensal_para_anual(Decimal("0.01"))
    assert abs(a - Decimal("0.12682503")) < Decimal("0.0001")
