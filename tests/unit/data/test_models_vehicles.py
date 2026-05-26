import tempfile
from decimal import Decimal
from pathlib import Path

import pytest

from app.data.database import Base, create_engine_for_sqlite, get_session_factory
from app.data.models import Vehicle


@pytest.fixture()
def session():
    with tempfile.TemporaryDirectory() as tmp:
        engine = create_engine_for_sqlite(Path(tmp) / "test.db")
        Base.metadata.create_all(engine)
        SessionLocal = get_session_factory(engine)
        with SessionLocal() as s:
            yield s
        engine.dispose()


def test_vehicle_has_new_fields(session):
    v = Vehicle(
        fonte="fipe", tipo="carro", marca="Honda", modelo="Civic",
        ano_modelo=2022, combustivel="Gasolina",
        valor_referencia=Decimal("115000"),
        cor="Prata", placa="ABC1234", odometro_km=32450, status="disponivel",
    )
    session.add(v)
    session.commit()
    session.refresh(v)

    assert v.cor == "Prata"
    assert v.placa == "ABC1234"
    assert v.odometro_km == 32450
    assert v.status == "disponivel"
    assert v.atualizado_em is not None
    assert v.criado_por is None


def test_vehicle_status_default(session):
    v = Vehicle(
        fonte="fipe", tipo="carro", marca="Toyota", modelo="Corolla",
        ano_modelo=2023, combustivel="Gasolina",
        valor_referencia=Decimal("145000"),
    )
    session.add(v)
    session.commit()
    session.refresh(v)
    assert v.status == "disponivel"
