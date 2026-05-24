from datetime import datetime

import pytest

from app.data.models import Client, User


def test_create_user(session) -> None:
    u = User(nome="Joao", pin_hash="$2b$12$fake", perfil="vendedor")
    session.add(u)
    session.commit()
    assert u.id is not None
    assert u.ativo is True


def test_create_client_with_creator(session) -> None:
    creator = User(nome="Admin", pin_hash="$2b$12$fake", perfil="admin")
    session.add(creator)
    session.commit()

    c = Client(
        nome="Maria",
        cpf_cnpj="12345678901",
        tipo="PF",
        criado_por=creator.id,
    )
    session.add(c)
    session.commit()
    assert c.id is not None
    assert c.criado_por == creator.id
