
from app.data.repositories import UserRepository


def test_create_and_get(session) -> None:
    repo = UserRepository(session)
    u = repo.create(nome="Joao", pin_hash="$2b$12$fake", perfil="vendedor")
    assert u.id is not None
    fetched = repo.get(u.id)
    assert fetched is not None
    assert fetched.nome == "Joao"


def test_list_active_only(session) -> None:
    repo = UserRepository(session)
    u1 = repo.create(nome="A", pin_hash="x", perfil="vendedor")
    u2 = repo.create(nome="B", pin_hash="x", perfil="vendedor")
    repo.deactivate(u2.id)
    actives = repo.list_active()
    assert len(actives) == 1
    assert actives[0].id == u1.id
