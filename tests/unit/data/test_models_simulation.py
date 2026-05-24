from datetime import date
from decimal import Decimal

import pytest

from app.data.models import (
    AmortizationRow,
    Client,
    Simulation,
    SimulationExtra,
    SimulationFee,
    User,
    Vehicle,
)


def test_create_simulation_with_extras_and_fees(session) -> None:
    u = User(nome="Joao", pin_hash="x", perfil="vendedor")
    session.add(u)
    session.commit()

    c = Client(nome="Maria", cpf_cnpj="12345678901", tipo="PF", criado_por=u.id)
    v = Vehicle(
        fonte="manual", tipo="carro", marca="Fiat", modelo="Mobi",
        ano_modelo=2024, combustivel="Gasolina",
        valor_referencia=Decimal("50000"),
    )
    session.add_all([c, v])
    session.commit()

    sim = Simulation(
        codigo="SIM-2026-00001",
        cliente_id=c.id,
        veiculo_id=v.id,
        criado_por=u.id,
        valor_veiculo=Decimal("50000"),
        valor_entrada=Decimal("10000"),
        pct_entrada=Decimal("0.2000"),
        prazo_meses=48,
        taxa_juros_mes=Decimal("0.0189"),
        taxa_juros_ano=Decimal("0.2520"),
        data_liberacao=date(2026, 1, 1),
        data_primeiro_venc=date(2026, 1, 31),
        dias_carencia=30,
        incluir_iof=True,
        iof_total=Decimal("0"),
        tarifas_total=Decimal("0"),
        extras_total_acumulado=Decimal("0"),
        valor_financiado=Decimal("40000"),
        valor_parcela=Decimal("1180"),
        total_pago=Decimal("56640"),
        total_juros=Decimal("16640"),
        pct_juros=Decimal("0.4160"),
        cet_mes=Decimal("0.0205"),
        cet_ano=Decimal("0.2750"),
        status="rascunho",
    )
    fee = SimulationFee(nome="Cadastro", valor=Decimal("500"), incluir_no_principal=True)
    extra = SimulationExtra(
        tipo="protecao_veicular",
        nome="Plano de protecao",
        valor_total=Decimal("80"),
        modalidade="mensal_continuo",
        duracao_meses=48,
        valor_por_parcela=Decimal("80.0000"),
        ordem=1,
    )
    sim.fees.append(fee)
    sim.extras.append(extra)
    session.add(sim)
    session.commit()

    assert sim.id is not None
    assert fee.simulation_id == sim.id
    assert extra.simulation_id == sim.id


def test_amortization_row_persists(session) -> None:
    u = User(nome="x", pin_hash="x", perfil="vendedor")
    session.add(u)
    v = Vehicle(fonte="manual", tipo="carro", marca="m", modelo="m", ano_modelo=2024, combustivel="G", valor_referencia=Decimal("1"))
    session.add(v)
    session.commit()
    sim = Simulation(
        codigo="SIM-2", cliente_id=None, veiculo_id=v.id, criado_por=u.id,
        valor_veiculo=Decimal("1"), valor_entrada=Decimal("0"), pct_entrada=Decimal("0"),
        prazo_meses=1, taxa_juros_mes=Decimal("0.01"), taxa_juros_ano=Decimal("0.12"),
        data_liberacao=date(2026, 1, 1), data_primeiro_venc=date(2026, 1, 31),
        dias_carencia=30, incluir_iof=True, iof_total=Decimal("0"),
        tarifas_total=Decimal("0"), extras_total_acumulado=Decimal("0"),
        valor_financiado=Decimal("1"), valor_parcela=Decimal("1.01"),
        total_pago=Decimal("1.01"), total_juros=Decimal("0.01"),
        pct_juros=Decimal("0.01"), cet_mes=Decimal("0.01"), cet_ano=Decimal("0.12"),
        status="rascunho",
    )
    row = AmortizationRow(
        numero_parcela=1, data_vencimento=date(2026, 1, 31),
        dias_periodo=30, saldo_anterior=Decimal("1"), juros=Decimal("0.01"),
        amortizacao=Decimal("1"), parcela=Decimal("1.01"), saldo_devedor=Decimal("0"),
        extras_total=Decimal("0"), parcela_total=Decimal("1.01"),
        ajuste_arredondamento=Decimal("0"),
    )
    sim.rows.append(row)
    session.add(sim)
    session.commit()
    assert row.id is not None
