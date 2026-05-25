import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from app.core.extras import Extra, ExtraModalidade
from app.data.database import Base, create_engine_for_sqlite, get_session_factory
from app.services.auth_service import AuthService
from app.services.client_service import ClientService
from app.services.proposal_service import ProposalService
from app.services.simulation_service import SimulationInputDTO, SimulationService


@pytest.mark.integration
def test_complete_flow_user_client_sim_proposal():
    with tempfile.TemporaryDirectory() as tmp:
        engine = create_engine_for_sqlite(Path(tmp) / "e2e.db")
        Base.metadata.create_all(engine)
        SessionLocal = get_session_factory(engine)
        with SessionLocal() as session:
            # 1. Vendedor cadastrado
            vendedor = AuthService(session).create_user("Joao", "123456", "vendedor")

            # 2. Cliente cadastrado
            client = ClientService(session).create_pf(
                nome="Maria", cpf="529.982.247-25", criado_por=vendedor.id,
            )

            # 3. Veiculo
            from app.data.models import Vehicle
            v = Vehicle(
                fonte="manual", tipo="carro", marca="Fiat", modelo="Mobi",
                ano_modelo=2024, combustivel="Gasolina", valor_referencia=Decimal("50000"),
            )
            session.add(v); session.commit()

            # 4. Simulacao com IOF + extras
            sim = SimulationService(session).run_and_save(SimulationInputDTO(
                criado_por=vendedor.id,
                cliente_id=client.id,
                veiculo_id=v.id,
                valor_veiculo=Decimal("50000"),
                valor_entrada=Decimal("10000"),
                prazo_meses=48,
                taxa_mensal=Decimal("0.0189"),
                data_liberacao=date(2026, 1, 1),
                data_primeiro_venc=date(2026, 1, 31),
                incluir_iof=True,
                tarifas=[],
                extras=[
                    Extra("ipva", "IPVA", Decimal("1800"),
                          ExtraModalidade.RATEIO_MESES, 12, 1),
                    Extra("protecao_veicular", "Protecao", Decimal("80"),
                          ExtraModalidade.MENSAL_CONTINUO, 48, 2),
                ],
            ))

            # 5. Proposta
            proposal = ProposalService(session).create(sim.id, gerado_por=vendedor.id)

            # Asserts
            assert sim.iof_total > Decimal("0")
            assert sim.cet_mes > Decimal("0.0189")  # CET > taxa due to IOF
            assert sim.extras_total_acumulado == Decimal("5640.00")  # 1800 + 80*48
            assert proposal.snapshot_json is not None
            import json
            snap = json.loads(proposal.snapshot_json)
            assert len(snap["cronograma"]) == 48
            assert len(snap["extras"]) == 2
            assert snap["cliente"]["nome"] == "Maria"
        engine.dispose()
