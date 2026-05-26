import tempfile
from decimal import Decimal
from pathlib import Path

import pytest

from app.data.database import Base, create_engine_for_sqlite, get_session_factory
from app.data.models import User
from app.integrations.fipe.schema import VehicleQuote


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
def svc(session):
    from app.services.vehicle_service import VehicleService
    return VehicleService(session)


@pytest.fixture()
def quote():
    return VehicleQuote(
        tipo="carro", marca="Honda", marca_id="6", modelo="Civic",
        modelo_id="1013", ano_modelo=2022, combustivel="Gasolina",
        codigo_fipe="001004-9", valor=Decimal("112000"),
        mes_referencia="maio de 2026", fonte="fipe_parallelum",
    )


def test_placa_formato_antigo_normalizado(svc, quote):
    v = svc.create_from_fipe(
        quote, cor="Prata", placa="abc-1234",
        odometro_km=None, valor_referencia=Decimal("115000"), criado_por=1,
    )
    assert v.placa == "ABC1234"


def test_placa_formato_mercosul(svc, quote):
    v = svc.create_from_fipe(
        quote, cor="Preto", placa="ABC1D23",
        odometro_km=None, valor_referencia=Decimal("115000"), criado_por=1,
    )
    assert v.placa == "ABC1D23"


def test_placa_invalida_levanta_erro(svc, quote):
    from app.services.vehicle_service import VehicleServiceError
    with pytest.raises(VehicleServiceError, match="inválida"):
        svc.create_from_fipe(
            quote, cor=None, placa="1234ABC",
            odometro_km=None, valor_referencia=Decimal("115000"), criado_por=1,
        )


def test_placa_duplicada_ativa_levanta_erro(svc, quote):
    from app.services.vehicle_service import VehicleServiceError
    svc.create_from_fipe(
        quote, cor="Prata", placa="ABC1234",
        odometro_km=None, valor_referencia=Decimal("115000"), criado_por=1,
    )
    with pytest.raises(VehicleServiceError, match="já cadastrada"):
        svc.create_from_fipe(
            quote, cor="Preto", placa="ABC1234",
            odometro_km=None, valor_referencia=Decimal("115000"), criado_por=1,
        )


def test_placa_liberada_apos_venda(svc, quote):
    v1 = svc.create_from_fipe(
        quote, cor="Prata", placa="ABC1234",
        odometro_km=None, valor_referencia=Decimal("115000"), criado_por=1,
    )
    svc.set_status(v1.id, "vendido", usuario_id=1)
    q2 = VehicleQuote(
        tipo="carro", marca="Honda", marca_id="6", modelo="Civic",
        modelo_id="1013", ano_modelo=2023, combustivel="Gasolina",
        codigo_fipe="001004-9", valor=Decimal("115000"),
        mes_referencia="maio de 2026", fonte="fipe_parallelum",
    )
    v2 = svc.create_from_fipe(
        q2, cor="Preto", placa="ABC1234",
        odometro_km=None, valor_referencia=Decimal("118000"), criado_por=1,
    )
    assert v2.id != v1.id
    assert v2.placa == "ABC1234"


def test_create_from_fipe_persiste_campos(svc, quote):
    v = svc.create_from_fipe(
        quote, cor="Prata", placa=None,
        odometro_km=32450, valor_referencia=Decimal("115000"), criado_por=1,
    )
    assert v.id is not None
    assert v.marca == "Honda"
    assert v.modelo == "Civic"
    assert v.valor_fipe == Decimal("112000")
    assert v.valor_referencia == Decimal("115000")
    assert v.cor == "Prata"
    assert v.odometro_km == 32450
    assert v.status == "disponivel"
    assert v.criado_por == 1
    assert v.fonte == "fipe_parallelum"


def test_create_manual_persiste_campos(svc):
    v = svc.create_manual(
        tipo="carro", marca="VW", modelo="Gol", ano_modelo=2020,
        combustivel="Flex", valor_referencia=Decimal("58000"),
        cor="Branco", placa="DEF5678", odometro_km=75000, criado_por=1,
    )
    assert v.id is not None
    assert v.fonte == "manual_cadastro"
    assert v.marca == "VW"
    assert v.placa == "DEF5678"
    assert v.status == "disponivel"


def test_set_status_invalido_levanta_erro(svc, quote):
    from app.services.vehicle_service import VehicleServiceError
    v = svc.create_from_fipe(
        quote, cor=None, placa=None,
        odometro_km=None, valor_referencia=Decimal("115000"), criado_por=1,
    )
    with pytest.raises(VehicleServiceError, match="inválido"):
        svc.set_status(v.id, "perdido", usuario_id=1)


def test_set_status_veiculo_inexistente_levanta_erro(svc):
    from app.services.vehicle_service import VehicleServiceError
    with pytest.raises(VehicleServiceError, match="não encontrado"):
        svc.set_status(99999, "disponivel", usuario_id=1)


def test_update_campos_fisicos(svc, quote):
    v = svc.create_from_fipe(
        quote, cor="Prata", placa=None,
        odometro_km=None, valor_referencia=Decimal("115000"), criado_por=1,
    )
    updated = svc.update(v.id, {"cor": "Preto", "odometro_km": 50000}, usuario_id=1)
    assert updated.cor == "Preto"
    assert updated.odometro_km == 50000


def test_update_ignora_campos_fipe(svc, quote):
    v = svc.create_from_fipe(
        quote, cor="Prata", placa=None,
        odometro_km=None, valor_referencia=Decimal("115000"), criado_por=1,
    )
    updated = svc.update(v.id, {"marca": "Toyota", "cor": "Cinza"}, usuario_id=1)
    assert updated.marca == "Honda"  # unchanged — not in allowed set
    assert updated.cor == "Cinza"


def test_set_status_valido(svc, quote):
    v = svc.create_from_fipe(
        quote, cor=None, placa=None,
        odometro_km=None, valor_referencia=Decimal("115000"), criado_por=1,
    )
    updated = svc.set_status(v.id, "reservado", usuario_id=1)
    assert updated.status == "reservado"


def test_refresh_fipe_atualiza_preco(svc, quote):
    v = svc.create_from_fipe(
        quote, cor=None, placa=None,
        odometro_km=None, valor_referencia=Decimal("115000"), criado_por=1,
    )
    new_quote = VehicleQuote(
        tipo="carro", marca="Honda", marca_id="6", modelo="Civic",
        modelo_id="1013", ano_modelo=2022, combustivel="Gasolina",
        codigo_fipe="001004-9", valor=Decimal("113000"),
        mes_referencia="junho de 2026", fonte="fipe_parallelum",
    )
    updated = svc.refresh_fipe(v.id, new_quote, usuario_id=1)
    assert updated.valor_fipe == Decimal("113000")
    assert updated.mes_referencia_fipe == "junho de 2026"
    assert updated.cor is None  # physical fields unchanged


def test_list_active_exclui_vendidos_e_fonte_manual(svc, quote):
    v1 = svc.create_from_fipe(
        quote, cor=None, placa=None,
        odometro_km=None, valor_referencia=Decimal("115000"), criado_por=1,
    )
    svc.set_status(v1.id, "vendido", usuario_id=1)
    q2 = VehicleQuote(
        tipo="carro", marca="Toyota", marca_id="59", modelo="Corolla",
        modelo_id="1002", ano_modelo=2023, combustivel="Flex",
        codigo_fipe="001002-3", valor=Decimal("145000"),
        mes_referencia="maio de 2026", fonte="fipe_parallelum",
    )
    v2 = svc.create_from_fipe(
        q2, cor=None, placa=None,
        odometro_km=None, valor_referencia=Decimal("148000"), criado_por=1,
    )
    result = svc.list_active()
    ids = [v.id for v in result]
    assert v2.id in ids
    assert v1.id not in ids


def test_list_active_search(svc, quote):
    svc.create_from_fipe(
        quote, cor="Prata", placa="ABC1234",
        odometro_km=None, valor_referencia=Decimal("115000"), criado_por=1,
    )
    assert len(svc.list_active(search="civic")) == 1
    assert len(svc.list_active(search="ferrari")) == 0


def test_get_simulations_vazio(svc, quote):
    v = svc.create_from_fipe(
        quote, cor=None, placa=None,
        odometro_km=None, valor_referencia=Decimal("115000"), criado_por=1,
    )
    assert svc.get_simulations(v.id) == []
