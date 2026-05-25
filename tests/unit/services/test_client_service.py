import tempfile
from pathlib import Path

import pytest

from app.data.database import Base, create_engine_for_sqlite, get_session_factory
from app.services.auth_service import AuthService
from app.services.client_service import ClientService, ClientServiceError


@pytest.fixture()
def session():
    with tempfile.TemporaryDirectory() as tmp:
        engine = create_engine_for_sqlite(Path(tmp) / "test.db")
        Base.metadata.create_all(engine)
        SessionLocal = get_session_factory(engine)
        with SessionLocal() as s:
            yield s
        engine.dispose()


def test_create_client_with_valid_cpf(session):
    u = AuthService(session).create_user("admin", "123456", "admin")
    svc = ClientService(session)
    c = svc.create_pf(
        nome="Joao Silva", cpf="529.982.247-25",
        criado_por=u.id, telefone="11999999999",
    )
    assert c.cpf_cnpj == "52998224725"


def test_create_client_invalid_cpf_raises(session):
    u = AuthService(session).create_user("admin", "123456", "admin")
    svc = ClientService(session)
    with pytest.raises(ClientServiceError):
        svc.create_pf(nome="X", cpf="00000000000", criado_por=u.id)
