from datetime import date
from decimal import Decimal

from app.core.amortization import (
    AmortizationMode,
    ExtraPayment,
    apply_extraordinary_amortizations,
)
from app.core.price_table import build_schedule


def test_reduzir_prazo_shortens_schedule() -> None:
    schedule = build_schedule(
        pv=Decimal("10000"),
        taxa_mensal=Decimal("0.015"),
        n=24,
        d1=30,
        data_liberacao=date(2026, 1, 1),
    )
    extras = [
        ExtraPayment(
            data=date(2026, 6, 1),
            valor=Decimal("3000"),
            modo=AmortizationMode.REDUZIR_PRAZO,
        )
    ]
    novo = apply_extraordinary_amortizations(
        schedule_original=schedule,
        pagamentos=extras,
        taxa_mensal=Decimal("0.015"),
    )
    assert len(novo.rows) < len(schedule.rows)
    # Rebuilt PMT must be <= original (customer pays no more per month)
    assert novo.pmt <= schedule.pmt


def test_reduzir_parcela_keeps_n_lowers_pmt() -> None:
    schedule = build_schedule(
        pv=Decimal("10000"),
        taxa_mensal=Decimal("0.015"),
        n=24,
        d1=30,
        data_liberacao=date(2026, 1, 1),
    )
    extras = [
        ExtraPayment(
            data=date(2026, 6, 1),
            valor=Decimal("3000"),
            modo=AmortizationMode.REDUZIR_PARCELA,
        )
    ]
    novo = apply_extraordinary_amortizations(
        schedule_original=schedule,
        pagamentos=extras,
        taxa_mensal=Decimal("0.015"),
    )
    assert novo.pmt < schedule.pmt


def test_schedule_pmt_is_uniform_pmt_not_last_row() -> None:
    # Payment on disbursement date => rows_paid=[], all rows are rebuilt segment.
    # Verifies Schedule.pmt carries the correct uniform PMT (not last row's adjusted parcela).
    schedule = build_schedule(
        pv=Decimal("10000"),
        taxa_mensal=Decimal("0.015"),
        n=24,
        d1=30,
        data_liberacao=date(2026, 1, 1),
    )
    extras = [
        ExtraPayment(
            data=date(2026, 1, 1),  # before first vencimento -> rows_paid is empty
            valor=Decimal("3000"),
            modo=AmortizationMode.REDUZIR_PARCELA,
        )
    ]
    novo = apply_extraordinary_amortizations(
        schedule_original=schedule,
        pagamentos=extras,
        taxa_mensal=Decimal("0.015"),
    )
    # All non-last rows should match novo.pmt exactly
    mid_row_parcelas = [r.parcela for r in novo.rows[:-1]]
    assert all(abs(p - novo.pmt) < Decimal("0.01") for p in mid_row_parcelas)
