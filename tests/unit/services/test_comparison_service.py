import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from app.data.database import Base, create_engine_for_sqlite, get_session_factory
from app.services.auth_service import AuthService
from app.services.comparison_service import ComparisonService
from app.services.simulation_service import SimulationInputDTO, SimulationService


@pytest.fixture()
def session():
    with tempfile.TemporaryDirectory() as tmp:
        engine = create_engine_for_sqlite(Path(tmp) / "test.db")
        Base.metadata.create_all(engine)
        SessionLocal = get_session_factory(engine)
        with SessionLocal() as s:
            yield s
        engine.dispose()


def test_compare_two_simulations(session):
    user = AuthService(session).create_user("vendedor", "123456", "vendedor")
    from app.data.models import Vehicle
    v = Vehicle(fonte="manual", tipo="carro", marca="Fiat", modelo="Mobi",
                ano_modelo=2024, combustivel="Gasolina", valor_referencia=Decimal("50000"))
    session.add(v); session.commit()

    sim_svc = SimulationService(session)
    sim_a = sim_svc.run_and_save(SimulationInputDTO(
        criado_por=user.id, cliente_id=None, veiculo_id=v.id,
        valor_veiculo=Decimal("50000"), valor_entrada=Decimal("10000"),
        prazo_meses=24, taxa_mensal=Decimal("0.015"),
        data_liberacao=date(2026, 1, 1), data_primeiro_venc=date(2026, 1, 31),
        incluir_iof=False, tarifas=[], extras=[],
    ))
    sim_b = sim_svc.run_and_save(SimulationInputDTO(
        criado_por=user.id, cliente_id=None, veiculo_id=v.id,
        valor_veiculo=Decimal("50000"), valor_entrada=Decimal("15000"),
        prazo_meses=24, taxa_mensal=Decimal("0.015"),
        data_liberacao=date(2026, 1, 1), data_primeiro_venc=date(2026, 1, 31),
        incluir_iof=False, tarifas=[], extras=[],
    ))

    comp_svc = ComparisonService(session)
    diff = comp_svc.diff(sim_a.id, sim_b.id)
    assert diff.delta_parcela < Decimal("0")  # B has higher entrada -> lower parcela
    assert diff.delta_total_pago < Decimal("0")
