import tempfile
from decimal import Decimal
from pathlib import Path

from app.data.database import Base, create_engine_for_sqlite, get_session_factory
from app.integrations.base import Ok
from app.integrations.fipe.cache import CachedFipeProvider
from app.integrations.fipe.schema import VehicleQuote


class FakeListProvider:
    name = "fake_list"
    calls = 0

    async def fetch(self, query):
        self.calls += 1
        return Ok([{"id": "1", "nome": "Acura"}])


class FakePriceProvider:
    name = "fake_price"
    calls = 0

    async def fetch(self, query):
        self.calls += 1
        return Ok(VehicleQuote(
            tipo="carro", marca="Fiat", marca_id="21", modelo="Mobi", modelo_id="1234",
            ano_modelo=2024, combustivel="Gasolina", codigo_fipe="001234-5",
            valor=Decimal("45230.00"), mes_referencia="maio de 2026",
            fonte="fake_price",
        ))


import pytest


@pytest.fixture()
def session_factory():
    with tempfile.TemporaryDirectory() as tmp:
        engine = create_engine_for_sqlite(Path(tmp) / "test.db")
        Base.metadata.create_all(engine)
        try:
            yield get_session_factory(engine)
        finally:
            engine.dispose()


async def test_list_cache_hits_after_first_call(session_factory):
    inner = FakeListProvider()
    cached = CachedFipeProvider(inner, session_factory)
    r1 = await cached.fetch({"action": "brands", "tipo": "carro"})
    r2 = await cached.fetch({"action": "brands", "tipo": "carro"})
    assert isinstance(r1, Ok) and isinstance(r2, Ok)
    assert r1.value == r2.value
    assert inner.calls == 1


async def test_price_cache_returns_vehicle_quote(session_factory):
    inner = FakePriceProvider()
    cached = CachedFipeProvider(inner, session_factory)
    q = {"action": "price", "tipo": "carro", "brand_id": "21", "model_id": "1234", "year_id": "2024-1"}
    r1 = await cached.fetch(q)
    r2 = await cached.fetch(q)
    assert isinstance(r1, Ok) and isinstance(r2, Ok)
    assert isinstance(r2.value, VehicleQuote)
    assert r2.value.valor == Decimal("45230.00")
    assert inner.calls == 1
