from datetime import date
from decimal import Decimal

from app.core.cet import compute_cet
from app.core.price_table import build_schedule


def test_cet_matches_taxa_when_no_iof_no_tarifas() -> None:
    schedule = build_schedule(
        pv=Decimal("10000"),
        taxa_mensal=Decimal("0.015"),
        n=24,
        d1=30,
        data_liberacao=date(2026, 1, 1),
    )
    cet = compute_cet(
        valor_liberado=Decimal("10000"),
        schedule=schedule,
        d1=30,
    )
    assert abs(cet.cet_mes - Decimal("0.015")) < Decimal("0.00001")


def test_cet_higher_than_taxa_with_iof() -> None:
    schedule = build_schedule(
        pv=Decimal("10500"),
        taxa_mensal=Decimal("0.015"),
        n=24,
        d1=30,
        data_liberacao=date(2026, 1, 1),
    )
    cet = compute_cet(
        valor_liberado=Decimal("10000"),
        schedule=schedule,
        d1=30,
    )
    assert cet.cet_mes > Decimal("0.015")
