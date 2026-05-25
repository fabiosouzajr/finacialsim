import json
import tempfile
from pathlib import Path

import pytest

from app.data.database import Base, create_engine_for_sqlite, get_session_factory
from app.data.models import AuditLog
from app.services.audit_service import AuditService


@pytest.fixture()
def session():
    with tempfile.TemporaryDirectory() as tmp:
        from app.data.models import User

        engine = create_engine_for_sqlite(Path(tmp) / "test.db")
        Base.metadata.create_all(engine)
        SessionLocal = get_session_factory(engine)
        with SessionLocal() as s:
            # Create a test user for FK constraint
            user = User(
                nome="Test User",
                pin_hash="hash",
                perfil="admin"
            )
            s.add(user)
            s.commit()
            yield s
        engine.dispose()


def test_log_creates_audit_entry(session):
    svc = AuditService(session)
    svc.log(usuario_id=None, acao="login", entidade="users", entidade_id=1,
            diff={"new": "value"})
    rows = session.query(AuditLog).all()
    assert len(rows) == 1
    assert rows[0].acao == "login"
    assert json.loads(rows[0].diff_json) == {"new": "value"}


def test_log_without_diff_stores_none(session):
    svc = AuditService(session)
    svc.log(usuario_id=1, acao="config_alterada")
    rows = session.query(AuditLog).all()
    assert rows[0].diff_json is None
