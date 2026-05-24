from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.data.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    pin_hash: Mapped[str] = mapped_column(String(120), nullable=False)
    perfil: Mapped[str] = mapped_column(String(20), nullable=False)  # vendedor|gerente|admin
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)
    ultimo_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    cpf_cnpj: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    tipo: Mapped[str] = mapped_column(String(2), nullable=False)  # PF|PJ
    rg: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    data_nasc: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    profissao: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    renda: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)
    telefone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    endereco_json: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    observacoes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    criado_por: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    fonte: Mapped[str] = mapped_column(String(40), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    marca: Mapped[str] = mapped_column(String(80), nullable=False)
    modelo: Mapped[str] = mapped_column(String(120), nullable=False)
    ano_modelo: Mapped[int] = mapped_column(Integer, nullable=False)
    combustivel: Mapped[str] = mapped_column(String(40), nullable=False)
    codigo_fipe: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    valor_fipe: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)
    valor_referencia: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    mes_referencia_fipe: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    snapshot_json: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)


class SimulationFee(Base):
    __tablename__ = "simulation_fees"

    id: Mapped[int] = mapped_column(primary_key=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id"), nullable=False)
    nome: Mapped[str] = mapped_column(String(80), nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    incluir_no_principal: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class SimulationExtra(Base):
    __tablename__ = "simulation_extras"

    id: Mapped[int] = mapped_column(primary_key=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(40), nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    valor_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    modalidade: Mapped[str] = mapped_column(String(30), nullable=False)
    duracao_meses: Mapped[int] = mapped_column(Integer, nullable=False)
    valor_por_parcela: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    ordem: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class AmortizationRow(Base):
    __tablename__ = "amortization_rows"

    id: Mapped[int] = mapped_column(primary_key=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id"), nullable=False, index=True)
    numero_parcela: Mapped[int] = mapped_column(Integer, nullable=False)
    data_vencimento: Mapped[date] = mapped_column(Date, nullable=False)
    dias_periodo: Mapped[int] = mapped_column(Integer, nullable=False)
    saldo_anterior: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    juros: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    amortizacao: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    parcela: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    saldo_devedor: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    extras_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    parcela_total: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)
    ajuste_arredondamento: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=Decimal("0"), nullable=False)


class ExtraordinaryAmortization(Base):
    __tablename__ = "extraordinary_amortizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    simulation_id: Mapped[int] = mapped_column(ForeignKey("simulations.id"), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    modo: Mapped[str] = mapped_column(String(30), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    aplicado_em: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)


class Simulation(Base):
    __tablename__ = "simulations"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    cliente_id: Mapped[Optional[int]] = mapped_column(ForeignKey("clients.id"), nullable=True)
    veiculo_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False)
    criado_por: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    valor_veiculo: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    valor_entrada: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    pct_entrada: Mapped[Decimal] = mapped_column(Numeric(7, 4), nullable=False)
    prazo_meses: Mapped[int] = mapped_column(Integer, nullable=False)
    taxa_juros_mes: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    taxa_juros_ano: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    data_liberacao: Mapped[date] = mapped_column(Date, nullable=False)
    data_primeiro_venc: Mapped[date] = mapped_column(Date, nullable=False)
    dias_carencia: Mapped[int] = mapped_column(Integer, nullable=False)
    incluir_iof: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    iof_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    tarifas_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    extras_total_acumulado: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    valor_financiado: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    valor_parcela: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    total_pago: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    total_juros: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    pct_juros: Mapped[Decimal] = mapped_column(Numeric(7, 4), nullable=False)
    cet_mes: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    cet_ano: Mapped[Decimal] = mapped_column(Numeric(10, 8), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    rules_snapshot_json: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    fees: Mapped[list[SimulationFee]] = relationship(cascade="all, delete-orphan")
    extras: Mapped[list[SimulationExtra]] = relationship(cascade="all, delete-orphan")
    rows: Mapped[list[AmortizationRow]] = relationship(
        cascade="all, delete-orphan",
        order_by="AmortizationRow.numero_parcela",
    )
