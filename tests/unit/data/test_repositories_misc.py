from datetime import date
from decimal import Decimal

from app.data.models import AmortizationRow, Simulation, SimulationFee, Vehicle
from app.data.repositories import (
    BusinessRuleRepository,
    ClientRepository,
    IndicatorRepository,
    SimulationRepository,
    UserRepository,
)


def test_client_create_and_find_by_cpf(session) -> None:
    u = UserRepository(session).create(nome="A", pin_hash="x", perfil="admin")
    repo = ClientRepository(session)
    c = repo.create(nome="Maria", cpf_cnpj="12345678901", tipo="PF", criado_por=u.id)
    assert c.id is not None
    found = repo.find_by_cpf_cnpj("12345678901")
    assert found is not None and found.id == c.id


def test_indicator_upsert(session) -> None:
    repo = IndicatorRepository(session)
    repo.upsert(codigo="SELIC", data_referencia=date(2026, 5, 23),
                valor=Decimal("0.10"), unidade="pct_aa", fonte="bcb_sgs")
    repo.upsert(codigo="SELIC", data_referencia=date(2026, 5, 23),
                valor=Decimal("0.11"), unidade="pct_aa", fonte="bcb_sgs")  # update
    latest = repo.get_latest("SELIC")
    assert latest is not None
    assert latest.valor == Decimal("0.11000000")


def test_business_rule_get(session) -> None:
    repo = BusinessRuleRepository(session)
    repo.set("entrada_minima_pct", "0.10", descricao="10%")
    val = repo.get("entrada_minima_pct")
    assert val == "0.10"
    val_none = repo.get("nao_existe")
    assert val_none is None


def test_simulation_create_and_get(session) -> None:
    u = UserRepository(session).create(nome="A", pin_hash="x", perfil="vendedor")
    v = Vehicle(fonte="manual", tipo="carro", marca="X", modelo="Y",
                ano_modelo=2024, combustivel="G", valor_referencia=Decimal("50000"))
    session.add(v)
    session.commit()

    sim = Simulation(
        codigo="SIM-TEST-001", veiculo_id=v.id, criado_por=u.id,
        valor_veiculo=Decimal("50000"), valor_entrada=Decimal("10000"),
        pct_entrada=Decimal("0.20"), prazo_meses=48,
        taxa_juros_mes=Decimal("0.0189"), taxa_juros_ano=Decimal("0.2520"),
        data_liberacao=date(2026, 1, 1), data_primeiro_venc=date(2026, 1, 31),
        dias_carencia=30, incluir_iof=True, iof_total=Decimal("0"),
        tarifas_total=Decimal("0"), extras_total_acumulado=Decimal("0"),
        valor_financiado=Decimal("40000"), valor_parcela=Decimal("1180"),
        total_pago=Decimal("56640"), total_juros=Decimal("16640"),
        pct_juros=Decimal("0.416"), cet_mes=Decimal("0.0205"),
        cet_ano=Decimal("0.275"), status="rascunho",
    )
    fee = SimulationFee(nome="Cadastro", valor=Decimal("500"), incluir_no_principal=True)
    row = AmortizationRow(
        numero_parcela=1, data_vencimento=date(2026, 1, 31), dias_periodo=30,
        saldo_anterior=Decimal("40000"), juros=Decimal("756"), amortizacao=Decimal("424"),
        parcela=Decimal("1180"), saldo_devedor=Decimal("39576"),
        extras_total=Decimal("0"), parcela_total=Decimal("1180"),
        ajuste_arredondamento=Decimal("0"),
    )
    sim.fees.append(fee)
    sim.rows.append(row)

    repo = SimulationRepository(session)
    saved = repo.create(sim)
    assert saved.id is not None
    assert saved.fees[0].simulation_id == saved.id

    loaded = repo.get(saved.id)
    assert loaded is not None
    assert len(loaded.rows) == 1

    c = ClientRepository(session).create(
        nome="Maria", cpf_cnpj="99988877766", tipo="PF", criado_por=u.id,
    )
    sim2 = Simulation(
        codigo="SIM-TEST-002", cliente_id=c.id, veiculo_id=v.id, criado_por=u.id,
        valor_veiculo=Decimal("50000"), valor_entrada=Decimal("10000"),
        pct_entrada=Decimal("0.20"), prazo_meses=48,
        taxa_juros_mes=Decimal("0.0189"), taxa_juros_ano=Decimal("0.2520"),
        data_liberacao=date(2026, 1, 1), data_primeiro_venc=date(2026, 1, 31),
        dias_carencia=30, incluir_iof=True, iof_total=Decimal("0"),
        tarifas_total=Decimal("0"), extras_total_acumulado=Decimal("0"),
        valor_financiado=Decimal("40000"), valor_parcela=Decimal("1180"),
        total_pago=Decimal("56640"), total_juros=Decimal("16640"),
        pct_juros=Decimal("0.416"), cet_mes=Decimal("0.0205"),
        cet_ano=Decimal("0.275"), status="rascunho",
    )
    repo.create(sim2)
    listed = repo.list_by_client(c.id)
    assert len(listed) == 1
    assert listed[0].codigo == "SIM-TEST-002"
