import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from app.data.database import Base, create_engine_for_sqlite, get_session_factory
from app.integrations.bacen.schema import IndicatorPoint
from app.integrations.base import Ok
from app.services.scheduler import _BACEN_CODES, _run_backup, _run_indicators_update


class FakeChain:
    def __init__(self):
        self.fetched: list[str] = []

    async def fetch(self, query):
        self.fetched.append(query["codigo"])
        return Ok([
            IndicatorPoint(
                codigo=query["codigo"],
                data_referencia=date.today(),
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
async def test_run_indicators_update_fetches_all_codes(session_factory):
    chain = FakeChain()
    await _run_indicators_update(session_factory, chain)
    assert set(chain.fetched) == set(_BACEN_CODES)


def test_run_backup_creates_file(session_factory):
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        db = tmp_path / "app.db"
        engine = create_engine_for_sqlite(db)
        Base.metadata.create_all(engine)
        sf = get_session_factory(engine)
        backup_dir = tmp_path / "backups"
        _run_backup(db, backup_dir, sf)
        assert backup_dir.exists()
        assert any(backup_dir.iterdir())
        engine.dispose()
