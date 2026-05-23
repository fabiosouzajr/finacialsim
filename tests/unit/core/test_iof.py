from datetime import date
from decimal import Decimal

from app.core.iof import DEFAULT_IOF_CONFIG, compute_financed_amount_with_iof, compute_iof
from app.core.price_table import build_schedule


def test_compute_iof_only_fixed_when_n_zero_carencia() -> None:
    schedule = build_schedule(
        pv=Decimal("1000"),
        taxa_mensal=Decimal("0.01"),
        n=1,
        d1=30,
        data_liberacao=date(2026, 1, 1),
    )
    iof = compute_iof(
        valor_financiado=Decimal("1000"),
        schedule=schedule,
        data_liberacao=date(2026, 1, 1),
        config=DEFAULT_IOF_CONFIG,
    )
    assert iof.fixo == Decimal("3.80")
    assert iof.diario == Decimal("2.46")
    assert iof.total == Decimal("6.26")


def test_compute_iof_caps_dias_at_365() -> None:
    schedule = build_schedule(
        pv=Decimal("10000"),
        taxa_mensal=Decimal("0.015"),
        n=30,
        d1=30,
        data_liberacao=date(2026, 1, 1),
    )
    iof = compute_iof(
        valor_financiado=Decimal("10000"),
        schedule=schedule,
        data_liberacao=date(2026, 1, 1),
        config=DEFAULT_IOF_CONFIG,
    )
    assert iof.diario > Decimal("0")


def test_iof_iteration_converges() -> None:
    result = compute_financed_amount_with_iof(
        pv_inicial=Decimal("10000"),
        taxa_mensal=Decimal("0.015"),
        n=12,
        d1=30,
        data_liberacao=date(2026, 1, 1),
        config=DEFAULT_IOF_CONFIG,
        incluir_iof=True,
    )
    assert result.valor_financiado > Decimal("10000")
    assert result.iof.total > Decimal("0")
    assert result.iteracoes <= 5


def test_iof_disabled_no_iteration() -> None:
    result = compute_financed_amount_with_iof(
        pv_inicial=Decimal("10000"),
        taxa_mensal=Decimal("0.015"),
        n=12,
        d1=30,
        data_liberacao=date(2026, 1, 1),
        config=DEFAULT_IOF_CONFIG,
        incluir_iof=False,
    )
    assert result.iof.total == Decimal("0.00")
    assert result.valor_financiado == Decimal("10000")
    assert result.iteracoes == 0
