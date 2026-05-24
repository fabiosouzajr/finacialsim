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
