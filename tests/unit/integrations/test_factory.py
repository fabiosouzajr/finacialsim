import tempfile
from pathlib import Path

import pytest

from app.data.database import Base, create_engine_for_sqlite, get_session_factory
from app.integrations.factory import build_bacen_chain, build_fipe_chain


@pytest.fixture()
def session_factory():
    with tempfile.TemporaryDirectory() as tmp:
        engine = create_engine_for_sqlite(Path(tmp) / "test.db")
        Base.metadata.create_all(engine)
        yield get_session_factory(engine)


def test_build_fipe_chain_has_two_providers(session_factory):
    chain = build_fipe_chain(session_factory)
    assert len(chain.providers) == 2


def test_build_bacen_chain_has_two_providers(session_factory):
    chain = build_bacen_chain(session_factory)
    assert len(chain.providers) == 2
