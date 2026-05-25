import json
import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from app.data.database import Base, create_engine_for_sqlite, get_session_factory
from app.services.auth_service import AuthService
from app.services.client_service import ClientService
from app.services.proposal_service import ProposalService
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


def test_create_proposal_persists_snapshot(session):
    user = AuthService(session).create_user("vendedor", "123456", "vendedor")
    client = ClientService(session).create_pf(
        nome="Maria", cpf="529.982.247-25", criado_por=user.id,
    )
    from app.data.models import Vehicle
    v = Vehicle(fonte="manual", tipo="carro", marca="F", modelo="M",
                ano_modelo=2024, combustivel="G", valor_referencia=Decimal("50000"))
    session.add(v); session.commit()
    sim = SimulationService(session).run_and_save(SimulationInputDTO(
        criado_por=user.id, cliente_id=client.id, veiculo_id=v.id,
        valor_veiculo=Decimal("50000"), valor_entrada=Decimal("10000"),
        prazo_meses=24, taxa_mensal=Decimal("0.015"),
        data_liberacao=date(2026, 1, 1), data_primeiro_venc=date(2026, 1, 31),
        incluir_iof=False, tarifas=[], extras=[],
    ))

    proposal = ProposalService(session).create(sim.id, gerado_por=user.id, validade_dias=7)
    assert proposal.codigo.startswith("PROP-")
    snap = json.loads(proposal.snapshot_json)
    assert snap["simulation"]["codigo"] == sim.codigo
    assert snap["simulation"]["valor_parcela"] is not None
    assert snap["cliente"]["nome"] == "Maria"


def test_create_clientless_proposal(session):
    user = AuthService(session).create_user("vendedor", "123456", "vendedor")
    from app.data.models import Vehicle
    v = Vehicle(fonte="manual", tipo="carro", marca="F", modelo="M",
                ano_modelo=2024, combustivel="G", valor_referencia=Decimal("50000"))
    session.add(v); session.commit()
    sim = SimulationService(session).run_and_save(SimulationInputDTO(
        criado_por=user.id, cliente_id=None, veiculo_id=v.id,
        valor_veiculo=Decimal("50000"), valor_entrada=Decimal("10000"),
        prazo_meses=24, taxa_mensal=Decimal("0.015"),
        data_liberacao=date(2026, 1, 1), data_primeiro_venc=date(2026, 1, 31),
        incluir_iof=False, tarifas=[], extras=[],
    ))

    proposal = ProposalService(session).create(sim.id, gerado_por=user.id)
    snap = json.loads(proposal.snapshot_json)
    assert snap["cliente"] is None
