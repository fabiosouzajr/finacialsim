import tempfile
from pathlib import Path

import pytest

from app.data.database import Base, create_engine_for_sqlite, get_session_factory
from app.services.auth_service import AuthError, AuthService, hash_pin


@pytest.fixture()
def session():
    with tempfile.TemporaryDirectory() as tmp:
        engine = create_engine_for_sqlite(Path(tmp) / "test.db")
        Base.metadata.create_all(engine)
        SessionLocal = get_session_factory(engine)
        with SessionLocal() as s:
            yield s
        engine.dispose()


def test_create_user_and_login(session):
    svc = AuthService(session)
    u = svc.create_user(nome="Joao", pin="123456", perfil="vendedor")
    assert u.id is not None
    logged = svc.login(user_id=u.id, pin="123456")
    assert logged.id == u.id


def test_login_wrong_pin_raises(session):
    svc = AuthService(session)
    u = svc.create_user(nome="A", pin="123456", perfil="vendedor")
    with pytest.raises(AuthError):
        svc.login(user_id=u.id, pin="000000")


def test_change_pin_works_with_old_pin(session):
    svc = AuthService(session)
    u = svc.create_user(nome="A", pin="111111", perfil="vendedor")
    svc.change_pin(user_id=u.id, old_pin="111111", new_pin="222222")
    svc.login(user_id=u.id, pin="222222")  # should not raise


def test_list_users_returns_active_only(session):
    svc = AuthService(session)
    svc.create_user(nome="Ativo", pin="123456", perfil="vendedor")
    u2 = svc.create_user(nome="Inativo", pin="123456", perfil="vendedor")
    from app.data.repositories import UserRepository
    UserRepository(session).deactivate(u2.id)
    users = svc.list_users()
    assert len(users) == 1
    assert users[0].nome == "Ativo"
