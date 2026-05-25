import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from app.core.amortization import AmortizationMode
from app.data.database import Base, create_engine_for_sqlite, get_session_factory
from app.services.amortization_service import AmortizationService, ExtraPaymentDTO
from app.services.auth_service import AuthService
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


def test_apply_partial_quitacao_reduces_pmt(session):
    user = AuthService(session).create_user("v", "123456", "vendedor")
    from app.data.models import Vehicle
    v = Vehicle(fonte="manual", tipo="carro", marca="F", modelo="M",
                ano_modelo=2024, combustivel="G", valor_referencia=Decimal("50000"))
    session.add(v); session.commit()

    sim_svc = SimulationService(session)
    sim = sim_svc.run_and_save(SimulationInputDTO(
        criado_por=user.id, cliente_id=None, veiculo_id=v.id,
        valor_veiculo=Decimal("50000"), valor_entrada=Decimal("10000"),
        prazo_meses=24, taxa_mensal=Decimal("0.015"),
        data_liberacao=date(2026, 1, 1), data_primeiro_venc=date(2026, 1, 31),
        incluir_iof=False, tarifas=[], extras=[],
    ))

    svc = AmortizationService(session)
    new_schedule = svc.apply(
        simulation_id=sim.id,
        pagamentos=[ExtraPaymentDTO(
            data=date(2026, 6, 1), valor=Decimal("5000"),
            modo=AmortizationMode.REDUZIR_PARCELA,
        )],
    )
    assert new_schedule.pmt < sim.valor_parcela
