"""ProposalService - builds Proposal record + snapshot JSON. PDF in Phase 6."""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.data.models import (
    AmortizationRow,
    Client,
    Proposal,
    Simulation,
    SimulationExtra,
    SimulationFee,
    Vehicle,
)
from app.services.audit_service import AuditService


def _next_codigo(session: Session) -> str:
    year = date.today().year
    count = session.query(Proposal).filter(Proposal.codigo.like(f"PROP-{year}-%")).count()
    return f"PROP-{year}-{count + 1:05d}"


def _decimal_to_str(v: Decimal) -> str:
    return str(v)


class ProposalService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.audit = AuditService(session)

    def create(self, simulation_id: int, gerado_por: int, validade_dias: int = 7) -> Proposal:
        sim = self.session.get(Simulation, simulation_id)
        if sim is None:
            raise ValueError("simulation not found")

        cliente = self.session.get(Client, sim.cliente_id) if sim.cliente_id is not None else None
        veiculo = self.session.get(Vehicle, sim.veiculo_id)
        fees = self.session.query(SimulationFee).filter_by(simulation_id=sim.id).all()
        extras = self.session.query(SimulationExtra).filter_by(simulation_id=sim.id).order_by(SimulationExtra.ordem).all()
        rows = (
            self.session.query(AmortizationRow)
            .filter_by(simulation_id=sim.id)
            .order_by(AmortizationRow.numero_parcela)
            .all()
        )

        cliente_snap = None
        if cliente is not None:
            cliente_snap = {
                "nome": cliente.nome, "cpf_cnpj": cliente.cpf_cnpj, "tipo": cliente.tipo,
                "telefone": cliente.telefone, "email": cliente.email,
                "endereco_json": cliente.endereco_json,
            }

        snapshot = {
            "simulation": {
                "codigo": sim.codigo,
                "valor_veiculo": _decimal_to_str(sim.valor_veiculo),
                "valor_entrada": _decimal_to_str(sim.valor_entrada),
                "pct_entrada": _decimal_to_str(sim.pct_entrada),
                "prazo_meses": sim.prazo_meses,
                "taxa_juros_mes": _decimal_to_str(sim.taxa_juros_mes),
                "taxa_juros_ano": _decimal_to_str(sim.taxa_juros_ano),
                "data_liberacao": sim.data_liberacao.isoformat(),
                "data_primeiro_venc": sim.data_primeiro_venc.isoformat(),
                "incluir_iof": sim.incluir_iof,
                "iof_total": _decimal_to_str(sim.iof_total),
                "tarifas_total": _decimal_to_str(sim.tarifas_total),
                "extras_total_acumulado": _decimal_to_str(sim.extras_total_acumulado),
                "valor_financiado": _decimal_to_str(sim.valor_financiado),
                "valor_parcela": _decimal_to_str(sim.valor_parcela),
                "total_pago": _decimal_to_str(sim.total_pago),
                "total_juros": _decimal_to_str(sim.total_juros),
                "cet_mes": _decimal_to_str(sim.cet_mes),
                "cet_ano": _decimal_to_str(sim.cet_ano),
            },
            "cliente": cliente_snap,
            "veiculo": {
                "marca": veiculo.marca, "modelo": veiculo.modelo,
                "ano_modelo": veiculo.ano_modelo, "combustivel": veiculo.combustivel,
                "codigo_fipe": veiculo.codigo_fipe,
                "valor_fipe": _decimal_to_str(veiculo.valor_fipe) if veiculo.valor_fipe else None,
                "mes_referencia_fipe": veiculo.mes_referencia_fipe,
            },
            "tarifas": [
                {"nome": f.nome, "valor": _decimal_to_str(f.valor),
                 "incluir_no_principal": f.incluir_no_principal}
                for f in fees
            ],
            "extras": [
                {"tipo": e.tipo, "nome": e.nome,
                 "valor_total": _decimal_to_str(e.valor_total),
                 "modalidade": e.modalidade, "duracao_meses": e.duracao_meses,
                 "valor_por_parcela": _decimal_to_str(e.valor_por_parcela)}
                for e in extras
            ],
            "cronograma": [
                {"numero": r.numero_parcela, "venc": r.data_vencimento.isoformat(),
                 "juros": _decimal_to_str(r.juros), "amortizacao": _decimal_to_str(r.amortizacao),
                 "parcela": _decimal_to_str(r.parcela), "extras": _decimal_to_str(r.extras_total),
                 "parcela_total": _decimal_to_str(r.parcela_total),
                 "saldo": _decimal_to_str(r.saldo_devedor)}
                for r in rows
            ],
        }

        proposal = Proposal(
            codigo=_next_codigo(self.session),
            simulation_id=sim.id,
            cliente_id=cliente.id if cliente else None,
            gerado_por=gerado_por,
            snapshot_json=json.dumps(snapshot),
            pdf_path=None,
            validade_dias=validade_dias,
        )
        self.session.add(proposal)
        self.session.commit()
        self.audit.log(
            "proposta_gerada",
            usuario_id=gerado_por,
            entidade="proposals",
            entidade_id=proposal.id,
        )
        return proposal
