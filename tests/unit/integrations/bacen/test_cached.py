import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from app.data.database import Base, create_engine_for_sqlite, get_session_factory
from app.data.repositories import IndicatorRepository
from app.integrations.bacen.cached import CachedBacenProvider
from app.integrations.bacen.schema import IndicatorPoint
from app.integrations.base import Ok


class FakeBacen:
    name = "fake"
    calls = 0

    async def fetch(self, query):
        self.calls += 1
        return Ok([
            IndicatorPoint(
                codigo="SELIC_META",
                data_referencia=date.today(),
                valor_fracao=Decimal("0.10500000"),
                unidade="pct_aa",
                fonte="fake",
            )
        ])


@pytest.fixture()
def session_factory():
    with tempfile.TemporaryDirectory() as tmp:
        engine = create_engine_for_sqlite(Path(tmp) / "test.db")
        Base.metadata.create_all(engine)
        try:
            yield get_session_factory(engine)
        finally:
            engine.dispose()


async def test_cached_writes_to_indicators_history(session_factory):
    cached = CachedBacenProvider(FakeBacen(), session_factory)
    r = await cached.fetch({"codigo": "SELIC_META"})
    assert r.is_ok
    with session_factory() as session:
        repo = IndicatorRepository(session)
        latest = repo.get_latest("SELIC_META")
        assert latest is not None
        assert latest.valor == Decimal("0.10500000")


async def test_cached_read_through_skips_network(session_factory):
    inner = FakeBacen()
    cached = CachedBacenProvider(inner, session_factory, ttl_horas=24)
    today = date.today()
    q = {"codigo": "SELIC_META", "data_inicial": today, "data_final": today}
    r1 = await cached.fetch(q)
    r2 = await cached.fetch(q)
    assert r1.is_ok and r2.is_ok
    assert inner.calls == 1  # second call served from indicators_history
