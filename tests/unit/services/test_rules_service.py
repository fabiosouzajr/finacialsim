import tempfile
from decimal import Decimal
from pathlib import Path

import pytest

from app.data.database import Base, create_engine_for_sqlite, get_session_factory
from app.data.repositories import BusinessRuleRepository
from app.services.rules_service import RulesService


@pytest.fixture()
def session():
    with tempfile.TemporaryDirectory() as tmp:
        engine = create_engine_for_sqlite(Path(tmp) / "test.db")
        Base.metadata.create_all(engine)
        SessionLocal = get_session_factory(engine)
        with SessionLocal() as s:
            # seed required rule
            BusinessRuleRepository(s).set("entrada_minima_pct", "0.10")
            BusinessRuleRepository(s).set("iof_fixo_pct", "0.0038")
            BusinessRuleRepository(s).set("incluir_iof_default", "true")
            yield s
        engine.dispose()


def test_decimal_default_value_when_missing(session):
    svc = RulesService(session)
    val = svc.get_decimal("nao_existe", default=Decimal("99"))
    assert val == Decimal("99")


def test_bool_value(session):
    svc = RulesService(session)
    val = svc.get_bool("incluir_iof_default", default=False)
    assert val is True


def test_decimal_value(session):
    svc = RulesService(session)
    val = svc.get_decimal("iof_fixo_pct", default=Decimal("0"))
    assert val == Decimal("0.0038")
