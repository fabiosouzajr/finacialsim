from decimal import Decimal

from app.core.price_table import compute_pmt


def test_compute_pmt_classic_price_d1_30() -> None:
    pmt = compute_pmt(
        pv=Decimal("10000"),
        taxa_mensal=Decimal("0.02"),
        n=12,
        d1=30,
    )
    assert abs(pmt - Decimal("945.60")) < Decimal("0.01")


def test_compute_pmt_one_installment() -> None:
    pmt = compute_pmt(
        pv=Decimal("1000"),
        taxa_mensal=Decimal("0.01"),
        n=1,
        d1=30,
    )
    assert pmt == Decimal("1010.00")


def test_compute_pmt_zero_rate() -> None:
    pmt = compute_pmt(
        pv=Decimal("12000"),
        taxa_mensal=Decimal("0"),
        n=12,
        d1=30,
    )
    assert pmt == Decimal("1000.00")


from datetime import date

from app.core.price_table import build_schedule


def test_build_schedule_invariants() -> None:
    schedule = build_schedule(
        pv=Decimal("10000"),
        taxa_mensal=Decimal("0.02"),
        n=12,
        d1=30,
        data_liberacao=date(2026, 1, 1),
    )
    assert len(schedule.rows) == 12
    assert schedule.rows[-1].saldo_devedor == Decimal("0.00")
    soma_amort = sum((r.amortizacao for r in schedule.rows), start=Decimal("0"))
    assert abs(soma_amort - Decimal("10000")) < Decimal("0.01")
    assert all(r.parcela > 0 for r in schedule.rows)


def test_build_schedule_first_row_juros_uses_d1() -> None:
    schedule = build_schedule(
        pv=Decimal("1000"),
        taxa_mensal=Decimal("0.01"),
        n=2,
        d1=30,
        data_liberacao=date(2026, 1, 1),
    )
    assert schedule.rows[0].juros == Decimal("10.00")
    assert schedule.rows[0].dias_periodo == 30
