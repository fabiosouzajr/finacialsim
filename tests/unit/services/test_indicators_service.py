import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from app.data.database import Base, create_engine_for_sqlite, get_session_factory
from app.data.models import IndicatorHistory
from app.integrations.bacen.schema import IndicatorPoint
from app.integrations.base import Ok
from app.services.indicators_service import IndicatorsService


class FakeChain:
    async def fetch(self, query):
        return Ok([
            IndicatorPoint(
                codigo=query["codigo"],
                data_referencia=date(2026, 5, 23),
                valor_fracao=Decimal("0.1050"),
                unidade="pct_aa",
                fonte="fake",
            )
        ])


@pytest.fixture()
def session_factory():
    with tempfile.TemporaryDirectory() as tmp:
        engine = create_engine_for_sqlite(Path(tmp) / "test.db")
        Base.metadata.create_all(engine)
        yield get_session_factory(engine)
        engine.dispose()


@pytest.mark.asyncio
async def test_update_indicator_persists(session_factory):
    svc = IndicatorsService(session_factory, bacen_chain=FakeChain())
    point = await svc.update_indicator("SELIC_META", date(2026, 5, 1), date(2026, 5, 31))
    assert point is not None
    assert point.valor_fracao == Decimal("0.1050")
    # check persisted
    with session_factory() as s:
        row = s.query(IndicatorHistory).filter_by(codigo="SELIC_META").first()
        assert row is not None
        assert row.valor == Decimal("0.1050")
        assert row.unidade == "pct_aa"
        assert row.fonte == "fake"
