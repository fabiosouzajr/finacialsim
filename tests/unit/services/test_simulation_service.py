import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from app.core.extras import Extra, ExtraModalidade
from app.data.database import Base, create_engine_for_sqlite, get_session_factory
from app.services.auth_service import AuthService
from app.services.simulation_service import (
    SimulationInputDTO,
    SimulationService,
    SimulationServiceError,
)


@pytest.fixture()
def session():
    with tempfile.TemporaryDirectory() as tmp:
        engine = create_engine_for_sqlite(Path(tmp) / "test.db")
        Base.metadata.create_all(engine)
        SessionLocal = get_session_factory(engine)
        with SessionLocal() as s:
            yield s
        engine.dispose()


def _make_vehicle(session):
    from app.data.models import Vehicle
    v = Vehicle(
        fonte="manual", tipo="carro", marca="Fiat", modelo="Mobi",
        ano_modelo=2024, combustivel="Gasolina",
        valor_referencia=Decimal("50000"),
    )
    session.add(v)
    session.commit()
    return v


def test_run_simulation_persists_and_returns(session):
    user = AuthService(session).create_user("vendedor", "123456", "vendedor")
    v = _make_vehicle(session)
    svc = SimulationService(session)
    sim = svc.run_and_save(
        SimulationInputDTO(
            criado_por=user.id,
            cliente_id=None,
            veiculo_id=v.id,
            valor_veiculo=Decimal("50000"),
            valor_entrada=Decimal("10000"),
            prazo_meses=24,
            taxa_mensal=Decimal("0.015"),
            data_liberacao=date(2026, 1, 1),
            data_primeiro_venc=date(2026, 1, 31),
            incluir_iof=True,
            tarifas=[],
            extras=[],
        )
    )
    assert sim.id is not None
    assert sim.codigo.startswith("SIM-")
    assert sim.valor_parcela > Decimal("0")
    assert sim.cet_mes > Decimal("0")
    # IOF was applied
    assert sim.iof_total > Decimal("0")
    # Amortization rows persisted
    from app.data.models import AmortizationRow
    rows = session.query(AmortizationRow).filter_by(simulation_id=sim.id).all()
    assert len(rows) == 24


def test_run_simulation_with_extras_persists_extras_total(session):
    user = AuthService(session).create_user("vendedor", "123456", "vendedor")
    v = _make_vehicle(session)
    svc = SimulationService(session)
    sim = svc.run_and_save(
        SimulationInputDTO(
            criado_por=user.id, cliente_id=None, veiculo_id=v.id,
            valor_veiculo=Decimal("50000"), valor_entrada=Decimal("10000"),
            prazo_meses=24, taxa_mensal=Decimal("0.015"),
            data_liberacao=date(2026, 1, 1), data_primeiro_venc=date(2026, 1, 31),
            incluir_iof=False,
            tarifas=[],
            extras=[
                Extra("ipva", "IPVA", Decimal("1200"), ExtraModalidade.RATEIO_MESES, 12, 1),
            ],
        )
    )
    # 12 first parcelas of 100 each = 1200
    assert sim.extras_total_acumulado == Decimal("1200.00")
    # First amortization row parcela_total includes 100
    from app.data.models import AmortizationRow
    rows = session.query(AmortizationRow).filter_by(simulation_id=sim.id).order_by(AmortizationRow.numero_parcela).all()
    assert rows[0].extras_total == Decimal("100.0000")
    assert rows[12].extras_total == Decimal("0.0000")


def test_validation_error_raises_simulation_service_error(session):
    user = AuthService(session).create_user("vendedor", "123456", "vendedor")
    v = _make_vehicle(session)
    svc = SimulationService(session)
    with pytest.raises(SimulationServiceError) as exc_info:
        svc.run_and_save(
            SimulationInputDTO(
                criado_por=user.id, cliente_id=None, veiculo_id=v.id,
                valor_veiculo=Decimal("50000"),
                valor_entrada=Decimal("100"),   # below 10% minimum
                prazo_meses=24, taxa_mensal=Decimal("0.015"),
                data_liberacao=date(2026, 1, 1), data_primeiro_venc=date(2026, 1, 31),
                incluir_iof=False, tarifas=[], extras=[],
            )
        )
    assert exc_info.value.issues
