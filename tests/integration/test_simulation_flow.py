"""End-to-end test exercising the whole core in one simulation."""

from datetime import date
from decimal import Decimal

import pytest

from app.core.cet import compute_cet
from app.core.extras import Extra, ExtraModalidade, compute_extras_per_parcela
from app.core.iof import DEFAULT_IOF_CONFIG, compute_financed_amount_with_iof
from app.core.validators import (
    DEFAULT_RULES,
    SimulationInput,
    ValidationLevel,
    validate_simulation,
)


@pytest.mark.integration
def test_full_simulation_with_iof_and_extras() -> None:
    valor_veiculo = Decimal("50000")
    valor_entrada = Decimal("10000")
    prazo = 48
    taxa = Decimal("0.0189")

    issues = validate_simulation(
        SimulationInput(
            valor_veiculo=valor_veiculo,
            valor_entrada=valor_entrada,
            prazo_meses=prazo,
            taxa_mensal=taxa,
            dias_carencia=30,
        ),
        DEFAULT_RULES,
    )
    assert not any(i.level is ValidationLevel.ERROR for i in issues)

    pv_inicial = valor_veiculo - valor_entrada
    financed = compute_financed_amount_with_iof(
        pv_inicial=pv_inicial,
        taxa_mensal=taxa,
        n=prazo,
        d1=30,
        data_liberacao=date(2026, 1, 1),
        config=DEFAULT_IOF_CONFIG,
        incluir_iof=True,
    )

    assert financed.iof.total > Decimal("0")
    assert len(financed.schedule.rows) == prazo

    cet = compute_cet(
        valor_liberado=pv_inicial,
        schedule=financed.schedule,
        d1=30,
    )
    assert cet.cet_mes > taxa

    extras = [
        Extra("protecao_veicular", "Plano de protecao", Decimal("80"),
              ExtraModalidade.MENSAL_CONTINUO, prazo, 1),
        Extra("ipva", "IPVA", Decimal("1800"), ExtraModalidade.RATEIO_MESES, 12, 2),
        Extra("emplacamento", "Emplacamento", Decimal("600"), ExtraModalidade.RATEIO_MESES, 12, 3),
    ]
    extras_per_parcela = compute_extras_per_parcela(extras, prazo)
    # First 12 parcelas (0-indexed 0..11): 80 + 150 + 50 = 280
    assert extras_per_parcela[0] == Decimal("280.00")
    # Parcelas 13+ (0-indexed 12+): 80 only
    assert extras_per_parcela[12] == Decimal("80.00")
