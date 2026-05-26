# tests/integration/test_vehicle_simulation_flow.py
"""Integration: vehicle registry → simulation → verify veiculo_id link."""
import tempfile
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from app.data.database import Base, create_engine_for_sqlite, get_session_factory
from app.data.models import User, Vehicle
from app.integrations.fipe.schema import VehicleQuote
from app.services.simulation_service import SimulationInputDTO, SimulationService
from app.services.vehicle_service import VehicleService


@pytest.fixture()
def session():
    with tempfile.TemporaryDirectory() as tmp:
        engine = create_engine_for_sqlite(Path(tmp) / "test.db")
        Base.metadata.create_all(engine)
        SessionLocal = get_session_factory(engine)
        with SessionLocal() as s:
            u = User(nome="Admin", pin_hash="x", perfil="admin")
            s.add(u)
            s.commit()
            yield s
        engine.dispose()


@pytest.fixture()
def quote():
    return VehicleQuote(
        tipo="carro", marca="Honda", marca_id="6", modelo="Civic",
        modelo_id="1013", ano_modelo=2022, combustivel="Gasolina",
        codigo_fipe="001004-9", valor=Decimal("112000"),
        mes_referencia="maio de 2026", fonte="fipe_parallelum",
    )


def test_simulate_with_registered_vehicle(session, quote):
    # Create vehicle
    svc = VehicleService(session)
    v = svc.create_from_fipe(
        quote, cor="Prata", placa=None,
        odometro_km=None, valor_referencia=Decimal("115000"), criado_por=1,
    )
    assert v.id is not None

    # Create simulation referencing the vehicle
    today = date.today()
    sim = SimulationService(session).run_and_save(SimulationInputDTO(
        criado_por=1,
        cliente_id=None,
        veiculo_id=v.id,
        valor_veiculo=Decimal("115000"),
        valor_entrada=Decimal("23000"),
        prazo_meses=48,
        taxa_mensal=Decimal("0.0189"),
        data_liberacao=today,
        data_primeiro_venc=today + timedelta(days=30),
        incluir_iof=True,
        tarifas=[],
        extras=[],
    ))

    assert sim.veiculo_id == v.id
    assert sim.valor_veiculo == Decimal("115000")

    # Verify get_simulations returns the linked simulation
    session.refresh(sim)
    sims = svc.get_simulations(v.id)
    assert len(sims) == 1
    assert sims[0].id == sim.id


def test_simulate_without_vehicle_creates_placeholder(session):
    """Legacy path: no vehicle selected → placeholder created."""
    today = date.today()

    # Create a placeholder manually (as simulacao.py does)
    v = Vehicle(
        fonte="manual", tipo="carro", marca="Manual", modelo="Veiculo",
        ano_modelo=today.year, combustivel="Gasolina",
        valor_referencia=Decimal("50000"),
    )
    session.add(v)
    session.commit()

    sim = SimulationService(session).run_and_save(SimulationInputDTO(
        criado_por=1,
        cliente_id=None,
        veiculo_id=v.id,
        valor_veiculo=Decimal("50000"),
        valor_entrada=Decimal("10000"),
        prazo_meses=36,
        taxa_mensal=Decimal("0.0189"),
        data_liberacao=today,
        data_primeiro_venc=today + timedelta(days=30),
        incluir_iof=False,
        tarifas=[],
        extras=[],
    ))

    assert sim.veiculo_id == v.id
    # Placeholder vehicle is fonte='manual'
    session.refresh(sim)
    linked_vehicle = session.get(Vehicle, sim.veiculo_id)
    assert linked_vehicle.fonte == "manual"
