from decimal import Decimal

from app.core.extras import Extra, ExtraModalidade, compute_extras_per_parcela


def test_mensal_continuo_all_parcelas() -> None:
    extras = [
        Extra(
            tipo="protecao_veicular",
            nome="Plano de protecao",
            valor_total=Decimal("80.00"),
            modalidade=ExtraModalidade.MENSAL_CONTINUO,
            duracao_meses=24,
            ordem=1,
        )
    ]
    result = compute_extras_per_parcela(extras, prazo_total=24)
    assert len(result) == 24
    assert all(v == Decimal("80.00") for v in result)


def test_rateio_meses_only_first_n() -> None:
    extras = [
        Extra(
            tipo="ipva",
            nome="IPVA anual",
            valor_total=Decimal("1800.00"),
            modalidade=ExtraModalidade.RATEIO_MESES,
            duracao_meses=12,
            ordem=2,
        )
    ]
    result = compute_extras_per_parcela(extras, prazo_total=48)
    assert all(v == Decimal("150.00") for v in result[:12])
    assert all(v == Decimal("0.00") for v in result[12:])
    assert len(result) == 48


def test_multiple_extras_sum_per_parcela() -> None:
    extras = [
        Extra(
            tipo="protecao_veicular",
            nome="Protecao",
            valor_total=Decimal("80.00"),
            modalidade=ExtraModalidade.MENSAL_CONTINUO,
            duracao_meses=24,
            ordem=1,
        ),
        Extra(
            tipo="ipva",
            nome="IPVA",
            valor_total=Decimal("1800.00"),
            modalidade=ExtraModalidade.RATEIO_MESES,
            duracao_meses=12,
            ordem=2,
        ),
    ]
    result = compute_extras_per_parcela(extras, prazo_total=24)
    assert all(v == Decimal("230.00") for v in result[:12])
    assert all(v == Decimal("80.00") for v in result[12:])


def test_unico_inicial_only_first_parcela() -> None:
    extras = [
        Extra(
            tipo="custom",
            nome="Taxa de adesao",
            valor_total=Decimal("500.00"),
            modalidade=ExtraModalidade.UNICO_INICIAL,
            duracao_meses=1,
            ordem=1,
        )
    ]
    result = compute_extras_per_parcela(extras, prazo_total=24)
    assert result[0] == Decimal("500.00")
    assert all(v == Decimal("0.00") for v in result[1:])


def test_rateio_last_installment_absorbs_rounding() -> None:
    # 1900 / 12 = 158.333... -> rounds to 158.33; last must get 158.37 to reach 1900.00
    extras = [
        Extra(
            tipo="ipva",
            nome="IPVA",
            valor_total=Decimal("1900.00"),
            modalidade=ExtraModalidade.RATEIO_MESES,
            duracao_meses=12,
            ordem=1,
        )
    ]
    result = compute_extras_per_parcela(extras, prazo_total=12)
    assert sum(result) == Decimal("1900.00")
